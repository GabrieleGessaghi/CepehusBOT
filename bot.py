import json
import random
import logging
import dyce_roll as dyce
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, ConversationHandler, Filters

TOKEN = None
with open("token.txt") as f:
    TOKEN = f.read().strip()

# character creation stages
GENDER, AGE, ORIGIN, RACE, TRAITS, CHARACTERISTICS, ABILITIES1, ABILITIES2,\
      FIRST_CAREER, START_CAREER, ADMISSION_FAILED, BASIC_TRAIN, SURVIVE, DEAD,\
        CAREER_GRADE_CHECK, GRADE_TRIAL, GET_GRADE, SELECT_ABILITY, PROMOTION, PROMOTION_TRIAL,\
            PROMOTION_RESULT, SELECT_PROMOTION_ABILITY, NO_PROMOTION, CAREER_ABILITY, DEAD= range(25)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# temporary user info during creation
tmp_user_data = {}
ability_counter = 3
selected_career = None
careers_number = 0
ability_list = ['Admin','Advocate','Animals','Carousing',
                    'Comms','Computer','Electronics','Engineering',
                    'Life Sciences','Linguistic','Mechanics','Medicine',
                    'Physical Sciences','Social Sciences','Space Sciences']


def main ():
    application = Updater(TOKEN, use_context= True)
    bot = application.dispatcher
    
    start_handler = CommandHandler('start', start)
    bot.add_handler(start_handler)

    help_handler = CommandHandler('help', help_f)
    bot.add_handler(help_handler)

    select_gender_handler = CommandHandler('gender', select_gender)
    bot.add_handler(select_gender_handler)

    set_age_handler = CommandHandler('age', set_age)
    bot.add_handler(set_age_handler)

    set_origin_handler = CommandHandler('origin', set_origin)
    bot.add_handler(set_origin_handler)

    calculate_characteristics_handler = CommandHandler('characteristics', calculate_characteristics)
    bot.add_handler(calculate_characteristics_handler)

    select_abilities1_handler = CommandHandler('abilities1', select_abilities1)
    bot.add_handler(select_abilities1_handler)

    select_abilities2_handler = CommandHandler('abilities2', select_abilities2)
    bot.add_handler(select_abilities2_handler)

    select_first_career_handler = CommandHandler('select_first_career', select_first_career)
    bot.add_handler(select_first_career_handler)
    
    start_first_career_handler = CommandHandler('start_first_career', start_career)
    bot.add_handler(start_first_career_handler)

    rejection_handler = CommandHandler('rejected', rejected)
    bot.add_handler(rejection_handler)

    basic_train_handler = CommandHandler('basic_train', basic_training)
    bot.add_handler(basic_train_handler)

    survive_trial_handler = CommandHandler('survive_trial', survival_trial)
    bot.add_handler(survive_trial_handler)

    career_grade_check_handler = CommandHandler('grade_check', career_grade_check)
    bot.add_handler(career_grade_check_handler)

    grade_trial_handler = CommandHandler('grade_trial', grade_trial)
    bot.add_handler(grade_trial_handler)

    get_grade_handler = CommandHandler('get_grade', get_grade)
    bot.add_handler(get_grade_handler)

    select_ability_handler = CommandHandler('select_ability', select_ability)
    bot.add_handler(select_ability_handler)

    start_promotion_path_handler = CommandHandler('start_promotion_path', start_promotion_path)
    bot.add_handler(start_promotion_path_handler)

    promotion_trial_handler = CommandHandler('promotion_trial', promotion_trial)
    bot.add_handler(promotion_trial_handler)

    promotion_result_handler = CommandHandler('promotion_result', promotion_result_check)
    bot.add_handler(promotion_result_handler)

    select_promotion_ability_handler = CommandHandler('select_promotion_ability', select_promotion_ability)
    bot.add_handler(select_promotion_ability_handler)

    no_promotion_handler = CommandHandler('no_promotion', no_promotion)
    bot.add_handler(no_promotion_handler)

    career_ability_handler = CommandHandler('career_ability', career_ability)
    bot.add_handler(career_ability_handler)

    dead_handler = CommandHandler('dead', cancel)
    bot.add_handler(dead_handler)


    character_creation_handler = ConversationHandler(
        entry_points=[(CommandHandler('create', create_character))],
        states={
            GENDER: [MessageHandler(Filters.text & ~Filters.command, select_gender)],
            AGE: [MessageHandler(Filters.text & ~Filters.command, set_age)],
            ORIGIN: [MessageHandler(Filters.text & ~Filters.command, set_origin)],
            CHARACTERISTICS: [MessageHandler(Filters.text & ~Filters.command, calculate_characteristics)],
            ABILITIES1: [MessageHandler(Filters.text & ~Filters.command, select_abilities1)],
            ABILITIES2: [MessageHandler(Filters.text & ~Filters.command, select_abilities2)],
            #RACE: [MessageHandler(Filters.text & ~Filters.command, select_race)],
            #TRAITS: [MessageHandler(Filters.text & ~Filters.command, select_traits)],
            FIRST_CAREER: [MessageHandler(Filters.text & ~Filters.command, select_first_career)],
            START_CAREER: [MessageHandler(Filters.text & ~Filters.command, start_career)],
            ADMISSION_FAILED: [MessageHandler(Filters.text & ~Filters.command, rejected)],
            BASIC_TRAIN: [MessageHandler(Filters.text & ~Filters.command, basic_training)],
            SURVIVE: [MessageHandler(Filters.text & ~Filters.command, survival_trial)],
            CAREER_GRADE_CHECK: [MessageHandler(Filters.text & ~Filters.command, career_grade_check)],
            GRADE_TRIAL: [MessageHandler(Filters.text & ~Filters.command, grade_trial)],
            GET_GRADE: [MessageHandler(Filters.text & ~Filters.command, get_grade)],
            SELECT_ABILITY: [MessageHandler(Filters.text & ~Filters.command, select_ability)],
            PROMOTION: [MessageHandler(Filters.text & ~Filters.command, start_promotion_path)],
            PROMOTION_TRIAL: [MessageHandler(Filters.text & ~Filters.command, promotion_trial)],
            PROMOTION_RESULT: [MessageHandler(Filters.text & ~Filters.command, promotion_result_check)],
            SELECT_PROMOTION_ABILITY: [MessageHandler(Filters.text & ~Filters.command, select_promotion_ability)],
            NO_PROMOTION: [MessageHandler(Filters.text & ~Filters.command, no_promotion)],
            NO_PROMOTION: [MessageHandler(Filters.text & ~Filters.command, career_ability)],
            DEAD : [MessageHandler(Filters.text & ~Filters.command, cancel)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    bot.add_handler(character_creation_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    bot.add_handler(unknown_handler)
    
    application.start_polling()
    application.idle()

    
#  /start
def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Ciao! Sono un bot che ti aiuterà a creare un personaggio per Cepheus Engine RPG. Iniziamo!')

# /help
def help_f(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,text="La lista dei comandi disponibili è presente nella tua tastiera")
    
# cancel character creation
def cancel(update: Update, context: CallbackContext):

    user_id = update.effective_user.name
    # deleting tmp info
    global tmp_user_data,ability_counter,careers_number,selected_career,ability_list
    try:
        del(tmp_user_data[f"{user_id}"])
        ability_counter = 3
        selected_career = None
        careers_number = 0
        ability_list = ['Admin','Advocate','Animals','Carousing',
                    'Comms','Computer','Electronics','Engineering',
                    'Life Sciences','Linguistic','Mechanics','Medicine',
                    'Physical Sciences','Social Sciences','Space Sciences']
    except KeyError:
        pass
    update.message.reply_text(
        'Creazione personaggio interrotta! \nPuoi creare un nuovo personaggio con i comando /create.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# start the process of character creation
def create_character(update: Update, context: CallbackContext):
    update.message.reply_text('Iniziamo a creare il personaggio, per prima cosa dagli un nome:')
    return GENDER

# gender selection
def select_gender(update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    character_name = update.message.text
    try:
        with open(f"json_files/users/{user_id}.json", "r") as fp:
            user_data = json.load(fp)
        character_name_key = "_".join(character_name.lower().split())
        if character_name_key in user_data.keys():
            update.message.reply_text("Mi dispiace ma questo nome è già stato preso, provane un'altro ...")
            return ConversationHandler.END
    except IOError:
        pass

    with open(f"json_files/character_sheet.json", "r") as fp:
        new_character = json.load(fp)
    
    new_character['name'] = character_name
    global tmp_user_data
    tmp_user_data[f"{user_id}"] = {}
    tmp_user_data[f"{user_id}"]["tmp_character"] = new_character

    update.message.reply_text(
        'Ottimo, seleziona il genere del tuo personaggio:',
        reply_markup= ReplyKeyboardMarkup(
            [['Uomo'], ['Donna']],
            on_time_keyboard= True, 
            input_field_placeholder='Seleziona il genere'
            )
        )
    return AGE

# set the age of the character
def set_age(update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    character_gender = update.message.text

    global tmp_user_data
    tmp_user_data[f"{user_id}"]["tmp_character"]["gender"] = character_gender

    update.message.reply_text("Quanti anni ha il tuo personaggio ?")
    return ORIGIN

# set the origin of the character
def set_origin(update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    character_age = update.message.text

    global tmp_user_data
    tmp_user_data[f"{user_id}"]["tmp_character"]["age"] = character_age

    update.message.reply_text("Da dove proviene il tuo personaggio (pianeta di origine)?")
    return CHARACTERISTICS

# calculate with dyce roll the characteristic
def calculate_characteristics (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    character_origin = update.message.text

    global tmp_user_data
    tmp_user_data[f"{user_id}"]["tmp_character"]["origin"] = character_origin
    
    update.message.reply_text(
        'Calcoliamo ora le caratteristiche usando 2D6',
        reply_markup= ReplyKeyboardMarkup(
            [['CALCOLA']],
            on_time_keyboard= True
            )
        )

    return ABILITIES1

# selection of first starting ability
def select_abilities1 (update: Update, context: CallbackContext):
    
    user_id = update.effective_user.name
    global tmp_user_data

    message_string = ""
    for key in tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]:
        if (key == 'PSI') or (key == 'PPU') :
            continue
        tmp_value = dyce.dice_roll(2,6)
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][key]["value"] = tmp_value
        tmp_modifier = int((tmp_value/3))-2
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][key]["modifier"] = tmp_modifier
        tmp_string = str(key) +' : value = '+str(tmp_value)+ ' || modifier = '+str(tmp_modifier)+'\n'
        message_string += tmp_string


    global ability_counter
    global ability_list
    
    reply_keyboard = []
    for ability in ability_list :
        reply_keyboard.append([ability])

    text_message = message_string+"\nSeleziona ora una abilità (rimanenti "+str(ability_counter)+"):"
    update.message.reply_text(
        text_message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
        one_time_keyboard=True,
        input_fiels_placeholder='Abilità')
    )

    return ABILITIES2

# selection of second and third starting abilities
def select_abilities2 (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    character_ability = update.message.text
    dict_entry = {"{}".format(character_ability):"0"}

    global tmp_user_data
    global ability_counter
    global ability_list

    #tmp_local = tmp_user_data[f"{user_id}"]
    tmp_user_data[f"{user_id}"]['tmp_character']['abilities'][character_ability] = 0
    ability_counter -= 1
    ability_list.remove(f"{character_ability}")

    if ability_counter > 0:
        reply_keyboard = []
        for ability in ability_list:
            reply_keyboard.append([ability])
        update.message.reply_text(
            'Seleziona una abilità (rimanenti '+str(ability_counter)+'):',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard,
            one_time_keyboard=True,
            input_fiels_placeholder='Abilità')
        )
        return ABILITIES2
    

    reply_keyboard = []
    with open(f"json_files/careers.json", "r") as fp:
        careers_info = json.load(fp)
        careers = [*careers_info]
    
    for career in careers:
        reply_keyboard.append([career])
    update.message.reply_text(
        'Seleziona la cariera che vuoi intraprendere, ricorda potresti essere rifiutato!',
        reply_markup= ReplyKeyboardMarkup(reply_keyboard,
                                          one_time_keyboard=True,
                                          input_field_placeholder='Seleziona carriera')
        )

    return FIRST_CAREER

# career selection and amission check
def select_first_career (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data, selected_career

    selected_career = update.message.text

    with open(f"json_files/careers.json", "r") as fp:
        careers_info = json.load(fp)[f"{selected_career}"]

    admission_check = careers_info["qualify"]

    roll = dyce.dice_roll(2,6)
    admission_check_attribute = list(admission_check.keys())
    admission_check_value = admission_check[admission_check_attribute[0]]
    admission_roll = roll + tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{admission_check_attribute[0]}"]["value"]+tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{admission_check_attribute[0]}"]["modifier"]


    if admission_roll >= admission_check_value:
        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"]["1"]["conscription_flag"] = 0
        update.message.reply_text(
            "Complimenti sei stato accettato, premi il bottone per cominciare la carriera !",
            reply_markup= ReplyKeyboardMarkup(
                [["Inizia la carriera da "+selected_career]],
                on_time_keyboard= True
                )
            )
        return START_CAREER
    else:
        # TODO rejection manage
        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"]["1"]["conscription_flag"] = 1 
        update.message.reply_text('Sei stato rifiutato !')
        return ADMISSION_FAILED

#saving career abilities and ask for basic training 
def start_career (update: Update, context: CallbackContext):
    user_id = update.effective_user.name

    global tmp_user_data, selected_career

    #career basic trainig     
    with open(f"json_files/careers.json", "r") as fp:
        careers_info = json.load(fp)[f"{selected_career}"]["service"]

    for key in careers_info:
        tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][careers_info[key]] = 0

    update.message.reply_text(
        "Premi il bottone per effettuare l'addestramento!",
        reply_markup= ReplyKeyboardMarkup(
                [['ADDESTRAMENTO DI BASE']],
                on_time_keyboard= True
                )
        )
    return BASIC_TRAIN

# career admision rejection
def rejected (update: Update, context: CallbackContext): 
    # TODO rejection manage
    update.message.reply_text('Diventa un ramingo o presentati alla circoscrizione !')
    return DEAD

# showing basic training result and ask for survive trial
def basic_training (update: Update, context: CallbackContext):
    user_id = update.effective_user.name

    global tmp_user_data,selected_career

    message_string = ""
    for key in tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"]:
        tmp_string = str(key) +' - '+str(tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][key])+'\n'
        message_string += tmp_string

    reply_string = "Hai completato l'addestramento di base per la seguente carriera: "+selected_career+"\n"+message_string+"\nPremi il bottone per fare la prova di sopravvivenza!"
    update.message.reply_text(
        reply_string,
        reply_markup= ReplyKeyboardMarkup(
                [['PROVA DI SOPRAVVIVENZA']],
                on_time_keyboard= True
                )
        )
    return SURVIVE
    
# first career survial trial and grade 0 assignment with relative abilities   
def survival_trial (update: Update, context: CallbackContext):
    user_id = update.effective_user.name

    global tmp_user_data,selected_career,careers_number
    with open(f"json_files/careers.json", "r") as fp:
        career_survival_check = json.load(fp)[f"{selected_career}"]["survive"]

    survival_check_attribute = list(career_survival_check.keys())
    survival_check_value = career_survival_check[survival_check_attribute[0]]

    roll = dyce.dice_roll(2,6)

    if roll == 2 :
        update.message.reply_text(
            'Hai fallito la prova di sopravvivenza perchè hai tirato un 2 naturale! \nPremi il bottone per eliminare il personaggio.',
            reply_markup= ReplyKeyboardMarkup(
                [['ELIMINA PERSONAGGIO']],
                on_time_keyboard= True
                )
        )                              
        return DEAD

    result = roll + tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{survival_check_attribute[0]}"]["value"]+tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{survival_check_attribute[0]}"]["modifier"]

    if result >= survival_check_value :
        with open(f"json_files/careers.json", "r") as fp:
            careers_grades_info = json.load(fp)[f"{selected_career}"]["grades"]["0"]
        
        career_grade_ability = careers_grades_info["abilities"]


        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"]["1"]["name"] = careers_grades_info["name"]
        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"]["1"]["grade"] = 0

        for key in career_grade_ability:    
            tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][key] = career_grade_ability[key]
        careers_number += 1
        update.message.reply_text(
            'Sei sopravvissuto, ti è stato assegnato il grado 0, premi il bottone per proseguire!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return CAREER_GRADE_CHECK
    else:
        update.message.reply_text(
            'Hai fallito la prova di sopravvivenza perchè non hai ottenuto il punteggio richiesto! \nPremi il bottone per eliminare il personaggio!',
            reply_markup= ReplyKeyboardMarkup(
                [['ELIMINA PERSONAGGIO']],
                on_time_keyboard= True
                )
        )                              
        return DEAD

# grade assign path after surviving, giving credits and goods of grade 0      
def career_grade_check (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data

    with open(f"json_files/careers.json", "r") as fp:
        career_info = json.load(fp)[f"{selected_career}"]
    
    career_survival_check = career_info["grades"]
    career_grade_credits = career_info["credits"]["1"]
    craeer_grade_goods = career_info["goods"]["1"]

    tmp_user_data[f"{user_id}"]["tmp_character"]["credits"] += career_grade_credits
    tmp_user_data[f"{user_id}"]["tmp_character"]["goods"].append(craeer_grade_goods)
    
    if tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] != 0:
        return PROMOTION
    
    if career_survival_check :
        update.message.reply_text(
            'La tua carriera offre dei gradi, vuoi una promozione?',
            reply_markup= ReplyKeyboardMarkup(
                [['SI'],['NO']],
                on_time_keyboard= True
                )
            )
        return GRADE_TRIAL
    else :
        update.message.reply_text(
            'Mi dispiace ma la tua carriera non offre ulteriori gradi!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return PROMOTION

# check if coscript and roll for grade assign
def grade_trial (update: Update, context: CallbackContext):
    user_id = update.effective_user.name

    user_choice = update.message.text

    if user_choice == 'NO':
        update.message.reply_text(
            'Nessun grado per te!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return PROMOTION
    
    global tmp_user_data, careers_number

    if tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["conscription_flag"] == 1:
        update.message.reply_text(
            'Mi dispiace non puoi ottenere nessun grado essendo stato coscritto!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return PROMOTION
    
    update.message.reply_text(
            'Tira per ottenere il grado (usa il bottone)!',
            reply_markup= ReplyKeyboardMarkup(
                [['OTTIENI IL GRADO']],
                on_time_keyboard= True
                )
            )
    return GET_GRADE

# check grade roll and increase grade if success 
def get_grade (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    
    global tmp_user_data,careers_number

    grade_roll = dyce.dice_roll(2,6)

    with open(f"json_files/careers.json", "r") as fp:
        career_info = json.load(fp)[f"{selected_career}"]

    
    career_grade_param_check = list(career_info["grade"].keys())
    career_grade_value_check = career_info["grade"][career_grade_param_check[0]]

    result = tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{career_grade_param_check[0]}"]["value"]+grade_roll+tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{career_grade_param_check[0]}"]["modifier"]

    if  result < career_grade_value_check:
        update.message.reply_text(
            'Mi dispiace non hai ottenuto il grado successivo!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return PROMOTION
    
    tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] += 1
    character_grade = tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"]
    tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["name"] = career_info["grades"][f"{character_grade}"]["name"]
    
    for key in career_info["grades"][f"{character_grade}"]["abilities"]:
        tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][key] = career_info["grades"][f"{character_grade}"]["abilities"][key]

    reply_keyboard = [['PERSONAL'], ['SERVICE'], ['SPECIALISTIC'], ['ADVANCED']]
    update.message.reply_text(
            'Seleziona la tabella abilità, verrà tirato un dado (1d6) e la abilità corrispondente aumenta di livello: ',
            reply_markup= ReplyKeyboardMarkup(
                reply_keyboard,
                on_time_keyboard= True
                )
            )
    print(tmp_user_data)
    return SELECT_ABILITY

# ask to to roll dyce for ability selection from selected table
def select_ability (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    selected_table = update.message.text.lower()
    global tmp_user_data

    dyce_roll = dyce.dice_roll (1,6)

    with open(f"json_files/careers.json", "r") as fp:
        career_table = json.load(fp)[f"{selected_career}"][f"{selected_table}"]

    selected_ability = career_table[f"{dyce_roll}"]

    if  selected_ability == 'FOR':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    elif selected_ability == 'DES':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    elif selected_ability == 'RES':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    elif selected_ability == 'INT':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    elif selected_ability == 'EDU':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    elif selected_ability == 'SOC':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    else :
        if selected_ability in tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"]:
            tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][f"{selected_ability}"] += 1
        else:
            tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][f"{selected_ability}"] = 0

    update.message.reply_text(
            'Il livello di '+selected_ability+' è aumentato!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
    return PROMOTION

# check if grade >0 and ask for promotion
def start_promotion_path (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data,careers_number

    if tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] == 0:
        update.message.reply_text(
            'Non ci sono promozioni disponibili, il tuo grado è 0!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return NO_PROMOTION
    
    with open(f"json_files/careers.json", "r") as fp:
        career_info = json.load(fp)[f"{selected_career}"]

    if career_info["grades"] :
        update.message.reply_text(
            'Vuoi una promozione?',
            reply_markup= ReplyKeyboardMarkup(
                [['SI'],['NO']],
                on_time_keyboard= True
                )
            )
        return PROMOTION_TRIAL
    else :
        update.message.reply_text(
            'La tua carriera non offre promozioni!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return NO_PROMOTION

# check user choice and ask for dyce roll
def promotion_trial (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    user_choice = update.message.text

    if user_choice == 'NO':
        return NO_PROMOTION
    
    update.message.reply_text(
            'Premi il bottone per fare la prova!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROVA DI PROMOZIONE']],
                on_time_keyboard= True
                )
            )
    return PROMOTION_RESULT


# check for promotion and give grade benefits
def promotion_result_check (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data,selected_career,careers_number

    with open(f"json_files/careers.json", "r") as fp:
        career_info = json.load(fp)[f"{selected_career}"]

    career_promotion_param = list(career_info["promotion"].keys())
    career_promotion_value = career_info["promotion"][career_promotion_param[0]]

    result = dyce.dice_roll(2,6) + tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{career_promotion_param[0]}"]["value"]+tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{career_promotion_param[0]}"]["modifier"]

    if result >= career_promotion_value:
        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] += 1
        character_grade = tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"]
        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["name"] = career_info["grades"][f"{character_grade}"]["name"]
    
        for key in career_info["grades"][f"{character_grade}"]["abilities"]:
            tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][key] = career_info["grades"][f"{character_grade}"]["abilities"][key]

        reply_keyboard = [['PERSONAL'], ['SERVICE'], ['SPECIALISTIC'], ['ADVANCED']]
        update.message.reply_text(
            'Hai superato la prova, aumenti di grado! \nSeleziona la tabella abilità, verrà tirato un dado (1d6) e la abilità corrispondente aumenta di livello:',
            reply_markup= ReplyKeyboardMarkup(
                reply_keyboard,
                on_time_keyboard= True
                )
            )
        return SELECT_PROMOTION_ABILITY
    else :
        update.message.reply_text(
            'Mi dispiace non hai superato la prova, non ci sono promozioni per te!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return NO_PROMOTION
    

# roll for ability and increase lvl of rolled one
def select_promotion_ability (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    selected_table = update.message.text.lower()
    global tmp_user_data

    dyce_roll = dyce.dice_roll (1,6)

    with open(f"json_files/careers.json", "r") as fp:
        career_table = json.load(fp)[f"{selected_career}"][f"{selected_table}"]

    selected_ability = career_table[f"{dyce_roll}"]

    if  selected_ability == 'FOR':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    elif selected_ability == 'DES':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    elif selected_ability == 'RES':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    elif selected_ability == 'INT':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    elif selected_ability == 'EDU':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    elif selected_ability == 'SOC':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{selected_ability}"]["value"] += 1
    else :
        if selected_ability in tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"]:
            tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][f"{selected_ability}"] += 1
        else:
            tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][f"{selected_ability}"] = 0

    update.message.reply_text(
            'Il livello di '+selected_ability+' è aumentato!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
    return CAREER_ABILITY


# no promotion path 
def no_promotion (update: Update, context: CallbackContext):
    # TODO
    context.bot.send_message(chat_id=update.effective_chat.id, text='Nessuna promozione per te!')


# start career ability path
def career_ability (update: Update, context: CallbackContext):
    # TODO
    context.bot.send_message(chat_id=update.effective_chat.id, text='Percorso abilità di carriera!')

# Unknown commands
def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Unknown command, try /help')


if __name__ == '__main__':
    main()