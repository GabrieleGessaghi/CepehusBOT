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
            PROMOTION_RESULT, SELECT_PROMOTION_ABILITY, NO_PROMOTION, CAREER_ABILITY, CAREER_ABILITY_ROLL,\
                  END_SERVICE_PERIOD, INCREASE_SERVICE_PERIOD, REENROLLMENT_PATH, RETIRE, RETIRE_CHOICE, CHANGE_CHOICE,\
                      END_CAREER, BENEFITS_TABLE_SELECTION, BENEFITS_ROLL, END_BENEFIT_PATH, DEAD= range(36)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# temporary user info during creation
tmp_user_data = {}
ability_counter = 3
benefits_counter = 0
selected_career = None
careers_number = 1
selected_table = None
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

    career_ability_roll_handler = CommandHandler('career_ability_roll', career_ability_roll)
    bot.add_handler(career_ability_roll_handler)

    end_service_period_handler = CommandHandler('end_service_period', end_service_period)
    bot.add_handler(end_service_period_handler)

    increase_service_period_handler = CommandHandler('increase_service_period', increase_service_period)
    bot.add_handler(increase_service_period_handler)

    reenrollment_path_handler = CommandHandler('re_enroll', re_enroll_trial)
    bot.add_handler(reenrollment_path_handler)

    retire_handler = CommandHandler('retire', retire)
    bot.add_handler(retire_handler)

    retire_choice_handler = CommandHandler('retire_choice', retire_choice)
    bot.add_handler(retire_choice_handler)

    change_choice_handler = CommandHandler('change_choice', change_choice)
    bot.add_handler(change_choice_handler)

    end_career_handler = CommandHandler('end_career', end_career)
    bot.add_handler(end_career_handler)

    benefits_table_selection_handler = CommandHandler('benefits_table', benefits_table_selection)
    bot.add_handler(benefits_table_selection_handler)

    benefits_roll_handler = CommandHandler('benefits_roll', benefits_roll)
    bot.add_handler(benefits_roll_handler)

    end_benefit_path_handler = CommandHandler('end_benefit_path', end_benefit_path)
    bot.add_handler(end_benefit_path_handler)

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
            CAREER_ABILITY: [MessageHandler(Filters.text & ~Filters.command, career_ability)],
            CAREER_ABILITY_ROLL: [MessageHandler(Filters.text & ~Filters.command, career_ability_roll)],
            END_SERVICE_PERIOD: [MessageHandler(Filters.text & ~Filters.command, end_service_period)],
            INCREASE_SERVICE_PERIOD: [MessageHandler(Filters.text & ~Filters.command, increase_service_period)],
            REENROLLMENT_PATH: [MessageHandler(Filters.text & ~Filters.command, re_enroll_trial)],
            RETIRE: [MessageHandler(Filters.text & ~Filters.command, retire)],
            RETIRE_CHOICE: [MessageHandler(Filters.text & ~Filters.command, retire_choice)],
            CHANGE_CHOICE: [MessageHandler(Filters.text & ~Filters.command, change_choice)],
            END_CAREER: [MessageHandler(Filters.text & ~Filters.command, end_career)],
            BENEFITS_TABLE_SELECTION: [MessageHandler(Filters.text & ~Filters.command, benefits_table_selection)],
            BENEFITS_ROLL: [MessageHandler(Filters.text & ~Filters.command, benefits_roll)],
            END_BENEFIT_PATH: [MessageHandler(Filters.text & ~Filters.command, end_benefit_path)],
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
        benefits_counter = 0
        selected_career = None
        careers_number = 1
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
    tmp_user_data[f"{user_id}"]["tmp_character"]["age"] = int(character_age)

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

        if tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["service_periods"] != 0:
            update.message.reply_text(
            'Sei sopravvissuto dopo esserti riarruolato!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )                              
            return CAREER_GRADE_CHECK


        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["name"] = careers_grades_info["name"]
        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] = 0

        for key in career_grade_ability:    
            tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][key] = career_grade_ability[key]
        
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
    global tmp_user_data,careers_number

    with open(f"json_files/careers.json", "r") as fp:
        career_info = json.load(fp)[f"{selected_career}"]
    
    career_grades = career_info["grades"]
    career_grade_credits = career_info["credits"]["1"]
    craeer_grade_goods = career_info["goods"]["1"]

    if tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] != 0:
        update.message.reply_text(
            'Il tuo grado attuale è: '+str(tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"]),
            reply_markup= ReplyKeyboardMarkup(
                [['VAI ALLE PROMOZIONI']],
                on_time_keyboard= True
                )
            )
        return PROMOTION

    tmp_user_data[f"{user_id}"]["tmp_character"]["credits"] += career_grade_credits

    if  craeer_grade_goods == 'FOR':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{craeer_grade_goods}"]["value"] += 1
    elif craeer_grade_goods == 'DES':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{craeer_grade_goods}"]["value"] += 1
    elif craeer_grade_goods == 'RES':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{craeer_grade_goods}"]["value"] += 1
    elif craeer_grade_goods == 'INT':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{craeer_grade_goods}"]["value"] += 1
    elif craeer_grade_goods == 'EDU':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{craeer_grade_goods}"]["value"] += 1
    elif craeer_grade_goods == 'SOC':
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{craeer_grade_goods}"]["value"] += 1
    else :
        if not craeer_grade_goods in tmp_user_data[f"{user_id}"]["tmp_character"]["goods"]:
            tmp_user_data[f"{user_id}"]["tmp_character"]["goods"].append(craeer_grade_goods)
    
    if career_grades :
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
        update.message.reply_text(
            'Hai scelto di non ottenere la promozione!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
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
    update.message.reply_text(
            'Nessuna promozione per te, prosegui con le abilità relative alla carriera',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
    return CAREER_ABILITY


# start career ability path
def career_ability (update: Update, context: CallbackContext):
    reply_keyboard = [['PERSONAL'], ['SERVICE'], ['SPECIALISTIC'], ['ADVANCED']]
    update.message.reply_text(
            'Passiamo alle abilità di carriera.\nSeleziona la tabella, verrà tirato un dado (1d6) e la abilità corrispondente aumenta di livello: ',
            reply_markup= ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard= True
                )
            )
    return CAREER_ABILITY_ROLL

# ability roll and increase lvl
def career_ability_roll (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data,selected_table,selected_career
    tmp_selected_table = update.message.text.lower()
    
    selected_table = tmp_selected_table

    is_second_ability = False

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

    with open(f"json_files/careers.json", "r") as fp:
        career_info = json.load(fp)[f"{selected_career}"]["grades"]
    
    if is_second_ability:
        update.message.reply_text(
            'Prosegui per terminare il periodo di servizio!',
                reply_markup= ReplyKeyboardMarkup(
                    [['PROSEGUI']],
                    one_time_keyboard=True
            )
        )
        return END_SERVICE_PERIOD

    if not career_info :
        is_second_ability= True
        update.message.reply_text(
            'La tua carriera non offre gradi e promozioni, puoi aumentare il livello di un altra abilità!',
            reply_markup= ReplyKeyboardMarkup(
                [['TIRA 1d6']],
                on_time_keyboard= True
                )
            )
        return CAREER_ABILITY_ROLL
    
    update.message.reply_text(
        selected_ability+' è aumentata di livello!\nLa tua carriera offre gradi e promozioni, prosegui per terminare il periodo di servizio!',
        reply_markup= ReplyKeyboardMarkup(
            [['PROSEGUI']],
            one_time_keyboard=True
        )
    )
    return END_SERVICE_PERIOD

# end first service period
def end_service_period (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data,careers_number

    tmp_user_data[f"{user_id}"]["tmp_character"]["age"] += 4

    #if tmp_user_data[f"{user_id}"]["tmp_character"]["age"] >= 34:
    #    roll = dyce.dice_roll(2,6)
        #TODO aging table

    #    return INCREASE_SERVICE_PERIOD

    update.message.reply_text(
            'Sono trascorsi 4 annni, hai terminato il periodo di servizio!',
            reply_markup= ReplyKeyboardMarkup(
                [['PRESEGUI']],
                on_time_keyboard= True
                )
            )
    return INCREASE_SERVICE_PERIOD   
    
# increase service period and go to re-enrollment
def increase_service_period (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data, careers_number

    tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["service_periods"] +=1
    
    update.message.reply_text(
            'Devi sostenere la prova per riarruolarti',
            reply_markup= ReplyKeyboardMarkup(
                [['Tira il dado (2d6)']],
                on_time_keyboard= True
                )
            )
    return REENROLLMENT_PATH


# re enrollment dyce roll and avaluating the result
def re_enroll_trial (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data, selected_career, careers_number

    roll = dyce.dice_roll(2,6)
    with open(f"json_files/careers.json", "r") as fp:
        career_info = json.load(fp)[f"{selected_career}"]

    career_enroll_value = career_info["reenrollment"]

    if roll == 12:
        update.message.reply_text(
            'Hai tirato un 12 naturale, devi servire per un altro periodo!',
            reply_markup= ReplyKeyboardMarkup(
                [['TORNA A SOPRAVVIVENZA']],
                on_time_keyboard= True
                )
            )
        return SURVIVE

    elif roll >= career_enroll_value:
        if roll != 12:
            if tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["service_periods"] == 7:
                update.message.reply_text(
                    'Sei al settimo periodo, devi ritirarti!',
                    reply_markup= ReplyKeyboardMarkup(
                        [['RITIRATI']],
                        on_time_keyboard= True
                    )
                )
                return RETIRE
            else :
                update.message.reply_text(
                    'Prova superata, vuoi ritirarti ?',
                    reply_markup= ReplyKeyboardMarkup(
                        [['SI'],['NO']],
                        on_time_keyboard= True
                    )
                )
                return RETIRE_CHOICE
                
    else :
        update.message.reply_text(
            'Non hai superato la prova, devi terminare la carriera!',
            reply_markup= ReplyKeyboardMarkup(
                [['TERMINA']],
                on_time_keyboard= True
                )
            )
        return END_CAREER

# user has retired and final touches
def retire (update: Update, context: CallbackContext):
    print (tmp_user_data)
    context.bot.send_message(chat_id=update.effective_chat.id, text='final touch')

# check user choice on retiring or changing career
def retire_choice (update: Update, context: CallbackContext):
    user_choice = update.message.text

    if user_choice == 'NO':
        update.message.reply_text(
                    'Vuoi cambiare carriera ?',
                    reply_markup= ReplyKeyboardMarkup(
                        [['SI'],['NO']],
                        on_time_keyboard= True
                    )
                )
        return CHANGE_CHOICE
    
    update.message.reply_text(
        'Hai scelto di ritirarti, verrai guidato ora hai passi conclusivi della creazione del tuo personaggio!',
        reply_markup= ReplyKeyboardMarkup(
            [['PROSEGUI']],
            one_time_keyboard= True
        )
    )

    return RETIRE

# check user choice on career change     
def change_choice (update: Update, context: CallbackContext):
    user_choice = update.message.text

    if user_choice == 'NO':
        update.message.reply_text(
                    'Premi il bottone per tornare alla sopravvivenza',
                    reply_markup= ReplyKeyboardMarkup(
                        [['TORNA A SOPRAVVIVENZA']],
                        on_time_keyboard= True
                    )
                )
        return SURVIVE
    
    update.message.reply_text(
        'Ottimo',
        reply_markup= ReplyKeyboardMarkup(
            [['TERMINA LA CARRIERA']],
            one_time_keyboard=True
        )
    )
    return END_CAREER

# get number of services and move to table selection
def end_career (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data, selected_career, careers_number, benefits_counter

    benefits_counter = tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["service_periods"]

    update.message.reply_text(
        'Avrai a disposizione '+str(benefits_counter)+' lanci!',
        reply_markup= ReplyKeyboardMarkup(
            [['PROSEGUI']],
            one_time_keyboard=True
        )
    )
    return BENEFITS_TABLE_SELECTION

# ask for table and go to roll
def benefits_table_selection (update: Update, context: CallbackContext):
    update.message.reply_text(
        'Scegli la tabella:',
        reply_markup= ReplyKeyboardMarkup(
            [['goods'],['credits']],
            one_time_keyboard=True
        )
    )
    return BENEFITS_ROLL

# roll for benefits and set tmp data
def benefits_roll (update: Update, context: CallbackContext):

    # TODO
    # max 3 credits benefits
    # +1 roll if grade > 5
    # add retirement salary if grade > 5

    user_id = update.effective_user.name
    selected_table = update.message.text 

    global tmp_user_data,benefits_counter
    roll = dyce.dice_roll(1,6)

    with open(f"json_files/careers.json", "r") as fp:
        career_info = json.load(fp)[f"{selected_career}"]

    benefit = career_info[f"{selected_table}"][f"{roll}"]
    benefit_string = ''

    if selected_table == 'credits':
        benefit_string = 'Hai ottenuto '+str(benefit)+' crediti!'
        tmp_user_data[f"{user_id}"]["tmp_character"]["credits"] += benefit
    else :

        if  benefit == 'FOR':
            benefit_string = benefit+' è aumentata di livello!'
            tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{benefit}"]["value"] += 1
        elif benefit == 'DES':
            benefit_string = benefit+' è aumentata di livello!'
            tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{benefit}"]["value"] += 1
        elif benefit == 'RES':
            benefit_string = benefit+' è aumentata di livello!'
            tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{benefit}"]["value"] += 1
        elif benefit == 'INT':
            benefit_string = benefit+' è aumentata di livello!'
            tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{benefit}"]["value"] += 1
        elif benefit == 'EDU':
            benefit_string = benefit+' è aumentata di livello!'
            tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{benefit}"]["value"] += 1
        elif benefit == 'SOC':
            benefit_string = benefit+' è aumentata di livello!'
            tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{benefit}"]["value"] += 1
        else :
            if not benefit in tmp_user_data[f"{user_id}"]["tmp_character"]["goods"]:
                tmp_user_data[f"{user_id}"]["tmp_character"]["goods"].append(benefit)
                benefit_string = 'Hai ottenuto '+str(benefit)+'!'

    benefits_counter -= 1

    if benefits_counter > 0:
        update.message.reply_text(
        benefit_string+'\nHai a disposizione ancora '+str(benefits_counter)+' lanci',
            reply_markup= ReplyKeyboardMarkup(
                [['CONTINUA']],
                one_time_keyboard=True
            )
        )
        return BENEFITS_TABLE_SELECTION
    
    update.message.reply_text(
        benefit_string+'\nHai terminato i lanci a disposizione, vuoi ritirarti ?',
        reply_markup= ReplyKeyboardMarkup(
            [['SI'],['NO']],
            one_time_keyboard= True
        )
    )

    return END_BENEFIT_PATH

# check user choice about retiring
def end_benefit_path (update: Update, context: CallbackContext):
    user_choice = update.message.text

    if user_choice == 'NO':
        #TODO next career
        print()

    update.message.reply_text(
        'Hai scelto di ritirarti, verrai guidato ora hai passi conclusivi della creazione del tuo personaggio!',
        reply_markup= ReplyKeyboardMarkup(
            [['PROSEGUI']],
            one_time_keyboard= True
        )
    )

    return RETIRE

# Unknown commands
def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Unknown command, try /help')


if __name__ == '__main__':
    main()


