import json
import random
import re
import os
import logging
import dyce_roll as dyce
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler

TOKEN = None
with open("token.txt") as f:
    TOKEN = f.read().strip()

# character creation stages
GENDER, AGE, ORIGIN, CHARACTERISTICS, ABILITIES1, ABILITIES2,\
      FIRST_CAREER, START_CAREER, ADMISSION_FAILED, BASIC_TRAIN, SURVIVE, DEAD,\
        CAREER_GRADE_CHECK, GRADE_TRIAL, GET_GRADE, SELECT_ABILITY, PROMOTION, PROMOTION_TRIAL,\
            PROMOTION_RESULT, SELECT_PROMOTION_ABILITY, NO_PROMOTION, CAREER_ABILITY, CAREER_ABILITY_ROLL,\
                  END_SERVICE_PERIOD,AGING, INCREASE_SERVICE_PERIOD, REENROLLMENT_PATH, RETIRE, RETIRE_CHOICE, CHANGE_CHOICE,\
                        END_CAREER, BENEFITS_TABLE_SELECTION, BENEFITS_ROLL, END_BENEFIT_PATH, START_NEXT_CAREER, NEXT_CAREER, BUY_EQUIPMENT, EQUIPMENT_CATEGORY,\
                            WEAPON_MENU, BUY_ITEM,ALIEN_CHOICE, TRAITS, DEAD, SAVE= range(44)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# temporary user info during creation
tmp_user_data = {}
ability_counter = 3
benefits_counter = 0
credits_counter = 3
selected_career = None
careers_number = 1
selected_table = None
main_menu = []
sub_menu = []
sub_sub_menu = [[],[],[],[]]
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

    show_handler = ConversationHandler(
        entry_points=[CommandHandler('show', show)],
        states={
            0: [MessageHandler(Filters.text & ~Filters.command, get_player_sheet)],
        },
    fallbacks=[],
    )
    bot.add_handler(show_handler)

    character_creation_handler = ConversationHandler(
        entry_points=[(CommandHandler('create', create_character))],
        states={
            GENDER: [MessageHandler(Filters.text & ~Filters.command, select_gender)],
            AGE: [MessageHandler(Filters.text & ~Filters.command, set_age)],
            ORIGIN: [MessageHandler(Filters.text & ~Filters.command, set_origin)],
            CHARACTERISTICS: [MessageHandler(Filters.text & ~Filters.command, calculate_characteristics)],
            ABILITIES1: [MessageHandler(Filters.text & ~Filters.command, select_abilities1)],
            ABILITIES2: [MessageHandler(Filters.text & ~Filters.command, select_abilities2)],
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
            AGING: [MessageHandler(Filters.text & ~Filters.command, aging)],
            INCREASE_SERVICE_PERIOD: [MessageHandler(Filters.text & ~Filters.command, increase_service_period)],
            REENROLLMENT_PATH: [MessageHandler(Filters.text & ~Filters.command, re_enroll_trial)],
            RETIRE: [MessageHandler(Filters.text & ~Filters.command, retire)],
            RETIRE_CHOICE: [MessageHandler(Filters.text & ~Filters.command, retire_choice)],
            CHANGE_CHOICE: [MessageHandler(Filters.text & ~Filters.command, change_choice)],
            END_CAREER: [MessageHandler(Filters.text & ~Filters.command, end_career)],
            BENEFITS_TABLE_SELECTION: [MessageHandler(Filters.text & ~Filters.command, benefits_table_selection)],
            BENEFITS_ROLL: [MessageHandler(Filters.text & ~Filters.command, benefits_roll)],
            END_BENEFIT_PATH: [MessageHandler(Filters.text & ~Filters.command, end_benefit_path)],
            START_NEXT_CAREER: [MessageHandler(Filters.text & ~Filters.command, start_next_career)],
            NEXT_CAREER: [MessageHandler(Filters.text & ~Filters.command, select_next_career)],
            BUY_EQUIPMENT: [MessageHandler(Filters.text & ~Filters.command, buy_equipment)],
            EQUIPMENT_CATEGORY: [MessageHandler(Filters.text & ~Filters.command, equipment_category)],
            WEAPON_MENU: [MessageHandler(Filters.text & ~Filters.command, weapon_menu)],
            BUY_ITEM: [MessageHandler(Filters.text & ~Filters.command, buy_item)],
            ALIEN_CHOICE: [MessageHandler(Filters.text & ~Filters.command, alien_choice)],
            TRAITS: [MessageHandler(Filters.text & ~Filters.command, traits)],
            DEAD : [MessageHandler(Filters.text & ~Filters.command, cancel)],
            SAVE: [MessageHandler(Filters.text & ~Filters.command, save)]
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
    context.bot.send_message(chat_id=update.effective_chat.id, text='Ciao! Sono un bot che ti aiuterà a creare un personaggio per Cepheus Engine RPG.\n\nPER UN CORRETTO FUNZIONAMENTO DEL BOT SI PREGA DI UTILIZZARE LE TASTIERE VIRTUALI PROPOSTE!')

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
            update.message.reply_text("Mi dispiace ma questo nome è già stato preso, ricomincia con /create")
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
            one_time_keyboard= True, 
            input_field_placeholder='Seleziona il genere'
            )
        )
    return AGE

# set the age of the character
def set_age(update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    character_gender = update.message.text

    global tmp_user_data
    if character_gender == 'Uomo':
        character_gender = 'Male'
    else:
        character_gender = 'Female'
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
                one_time_keyboard= True
                )
            )
        return START_CAREER
    else:
        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"]["1"]["conscription_flag"] = 0
        update.message.reply_text(
            'Sei stato rifiutato !\n Premi il bottone per continuare.',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                 one_time_keyboard = True
            )
            )
        return ADMISSION_FAILED

#saving career abilities and ask for basic training 
def start_career (update: Update, context: CallbackContext):
    user_id = update.effective_user.name

    global tmp_user_data, selected_career

    #career basic trainig     
    with open(f"json_files/careers.json", "r") as fp:
        careers_info = json.load(fp)[f"{selected_career}"]["service"]

    for key in careers_info:
        if careers_info[key] in tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"].keys():
             tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][careers_info[key]] += 1
        else:
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
    global selected_career

    selected_career = 'Drifter'
    update.message.reply_text(
        'Per questo periodo dovrai intraprendere la carriera da ramingo!',
        reply_markup= ReplyKeyboardMarkup(
            [['Drifter']],
            one_time_keyboard=True
        )
        )
    return START_CAREER

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
            if key in tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"].keys() :
                tmp_user_data[f"{user_id}"]["tmp_character"]["abilities"][key] += career_grade_ability[key]
            else:
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
    
    if career_info["grade"] :
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

    if tmp_user_data[f"{user_id}"]["tmp_character"]["age"] >= 34:
        update.message.reply_text(
            'Hai più di 34 anni, tira sulla tabella di invecchiamento!',
            reply_markup= ReplyKeyboardMarkup(
                [['TIRA 2D6']],
                on_time_keyboard= True
                )
            )
        return AGING  

    update.message.reply_text(
            'Sono trascorsi 4 annni, hai terminato il periodo di servizio!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
    return INCREASE_SERVICE_PERIOD   


def aging (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data, careers_number

    service_periods = tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["service_periods"]

    roll = dyce.dice_roll(2,6) - service_periods
    if roll == -6 :
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]["FOR"]["value"] -= 2
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]["DES"]["value"] -= 2
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]["RES"]["value"] -= 2
        mental = random.choice(["INT","EDU","SOC"])
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][mental]["value"] -= 1
        update.message.reply_text(
            'FOR, DES e RES sono diminuite di 2!\n'+mental+' è diminuita di 1!\nHai terminato il periodo di servizio!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return INCREASE_SERVICE_PERIOD
    elif roll == -5:
        phisical1 = random.choice(["FOR","DES","RES"])
        phisical2 = phisical1
        while phisical2 == phisical1:
            phisical2 = random.choice(["FOR","DES","RES"])

        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical1]["value"] -= 2
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical2]["value"] -= 2
        update.message.reply_text(
            phisical1+' e '+phisical2+' sono diminuite di 2!\nHai terminato il periodo di servizio!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return INCREASE_SERVICE_PERIOD
    elif roll == -4:
        phisical1 = random.choice(["FOR","DES","RES"])
        phisical2 = phisical1
        phisical3 = phisical1
        while phisical2 == phisical1:
            phisical2 = random.choice(["FOR","DES","RES"])
        while phisical3 == phisical2 or phisical3 == phisical1:
            phisical3 = random.choice(["FOR","DES","RES"])

        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical1]["value"] -= 2
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical2]["value"] -= 2
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical3]["value"] -= 1
        update.message.reply_text(
            phisical1+' e '+phisical2+' sono diminuite di 2!\n'+phisical3+' è diminuita di 1!\nHai terminato il periodo di servizio!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return INCREASE_SERVICE_PERIOD
    elif roll == -3:
        phisical1 = random.choice(["FOR","DES","RES"])
        phisical2 = phisical1
        phisical3 = phisical1
        while phisical2 == phisical1:
            phisical2 = random.choice(["FOR","DES","RES"])
        while phisical3 == phisical2 or phisical3 == phisical1:
            phisical3 = random.choice(["FOR","DES","RES"])

        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical1]["value"] -= 2
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical2]["value"] -= 1
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical3]["value"] -= 1
        update.message.reply_text(
            phisical2+' e '+phisical3+' sono diminuite di 2!\n'+phisical1+' è diminuita di 2!\nHai terminato il periodo di servizio!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return INCREASE_SERVICE_PERIOD
    elif roll == -2:
        phisical1 = random.choice(["FOR","DES","RES"])
        phisical2 = phisical1
        phisical3 = phisical1
        while phisical2 == phisical1:
            phisical2 = random.choice(["FOR","DES","RES"])
        while phisical3 == phisical2 or phisical3 == phisical1:
            phisical3 = random.choice(["FOR","DES","RES"])

        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical1]["value"] -= 1
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical2]["value"] -= 1
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical3]["value"] -= 1
        update.message.reply_text(
            phisical1+', '+phisical2+' e '+phisical3+' sono diminuite di 1!\nHai terminato il periodo di servizio!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return INCREASE_SERVICE_PERIOD
    elif roll == -1:
        phisical1 = random.choice(["FOR","DES","RES"])
        phisical2 = phisical1
        while phisical2 == phisical1:
            phisical2 = random.choice(["FOR","DES","RES"])

        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical1]["value"] -= 1
        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical2]["value"] -= 1
        update.message.reply_text(
            phisical1+' e '+phisical2+' sono diminuite di 1!\nHai terminato il periodo di servizio!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return INCREASE_SERVICE_PERIOD
    elif roll == 0:
        phisical1 = random.choice(["FOR","DES","RES"])

        tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][phisical1]["value"] -= 1
        update.message.reply_text(
            phisical1+' è diminuita di 1!\nHai terminato il periodo di servizio!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                on_time_keyboard= True
                )
            )
        return INCREASE_SERVICE_PERIOD
    elif roll >= 1:
        update.message.reply_text(
        'Nessun effetto!\nHai terminato il periodo di servizio!',
        reply_markup= ReplyKeyboardMarkup(
            [['PROSEGUI']],
            on_time_keyboard= True
            )
        )
        return INCREASE_SERVICE_PERIOD

# FOR DES RES PHISICAL CHARCTERISTICS
# INT EDU SOC MENTAL CHARCTERISTICS


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
    update.message.reply_text(
            "Premi il bottone per iniziare a comprare l'equipaggiamento",
            reply_markup= ReplyKeyboardMarkup(
                [['COMPRA EQUIPAGGIAMENTO']],
                on_time_keyboard= True
                )
            )
    return BUY_EQUIPMENT

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
    payout = 0
    if tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] >= 5:
        benefits_counter += 1
        if tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] == 5:
            payout = 10000
        elif tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] == 6:
            payout = 12000
        elif tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] == 7:
            payout = 14000
        elif tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"] == 8:
            payout = 16000
        else :
            payout = 2000*(tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["grade"]-8)

        update.message.reply_text(
            'Hai ottenuto una pensione di '+payout+' Cr!\nAvrai a disposizione '+str(benefits_counter)+' lanci!\nRicorda che potrai tirare sulla tabella CREDITS solo 3 volte per tutta la creazione del personaggio!',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                one_time_keyboard=True
            )
        )
        return BENEFITS_TABLE_SELECTION

    update.message.reply_text(
        'Avrai a disposizione '+str(benefits_counter)+' lanci!\nRicorda che potrai tirare sulla tabella CREDITS solo 3 volte per tutta la creazione del personaggio!',
        reply_markup= ReplyKeyboardMarkup(
            [['PROSEGUI']],
            one_time_keyboard=True
        )
    )
    return BENEFITS_TABLE_SELECTION

# ask for table and go to roll
def benefits_table_selection (update: Update, context: CallbackContext):
    global credits_counter
    if credits_counter == 0:
        update.message.reply_text(
        'Hai esaurito i lanci sulla tabella CREDITS!\nTira sulla tabella GOODS:',
            reply_markup= ReplyKeyboardMarkup(
                [['goods']],
                one_time_keyboard=True
            )
        )
        return BENEFITS_ROLL
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

    user_id = update.effective_user.name
    selected_table = update.message.text 

    global tmp_user_data,benefits_counter, credits_counter
    roll = dyce.dice_roll(1,6)

    with open(f"json_files/careers.json", "r") as fp:
        career_info = json.load(fp)[f"{selected_career}"]

    benefit = career_info[f"{selected_table}"][f"{roll}"]
    benefit_string = ''

    if selected_table == 'credits':
        credits_counter -= 1
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
        update.message.reply_text(
            'Prosegui per iniziare una nuova carriera.',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                one_time_keyboard=True
            )
        )
        return START_NEXT_CAREER

    update.message.reply_text(
        'Hai scelto di ritirarti, verrai guidato ora hai passi conclusivi della creazione del tuo personaggio!',
        reply_markup= ReplyKeyboardMarkup(
            [['PROSEGUI']],
            one_time_keyboard= True
        )
    )
    return RETIRE


def start_next_career (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global careers_number, selected_career
    careers_number += 1
    
    reply_keyboard = []
    with open(f"json_files/careers.json", "r") as fp:
        careers_info = json.load(fp)
        careers = [*careers_info]

    careers.remove(selected_career)

    for career in careers:
        reply_keyboard.append([career])

    update.message.reply_text(
        'Seleziona la cariera che vuoi intraprendere, ricorda potresti essere rifiutato!',
        reply_markup= ReplyKeyboardMarkup(reply_keyboard,
                                          one_time_keyboard=True,
                                          input_field_placeholder='Seleziona carriera')
        )

    return NEXT_CAREER

def select_next_career (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data, selected_career, careers_number

    selected_career = update.message.text

    with open(f"json_files/careers.json", "r") as fp:
        careers_info = json.load(fp)[f"{selected_career}"]

    admission_check = careers_info["qualify"]

    roll = dyce.dice_roll(2,6)
    admission_check_attribute = list(admission_check.keys())
    admission_check_value = admission_check[admission_check_attribute[0]]
    admission_roll = roll + tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{admission_check_attribute[0]}"]["value"]+tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{admission_check_attribute[0]}"]["modifier"]


    if admission_roll >= admission_check_value:
        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["conscription_flag"] = 0
        update.message.reply_text(
            "Complimenti sei stato accettato, premi il bottone per cominciare la carriera !",
            reply_markup= ReplyKeyboardMarkup(
                [["Inizia la carriera da "+selected_career]],
                one_time_keyboard= True
                )
            )
        return START_CAREER
    else:
        tmp_user_data[f"{user_id}"]["tmp_character"]["careers"][f"{careers_number}"]["conscription_flag"] = 0
        update.message.reply_text(
            'Sei stato rifiutato !\n Premi il bottone per continuare.',
            reply_markup= ReplyKeyboardMarkup(
                [['PROSEGUI']],
                 one_time_keyboard = True
            )
            )
        return ADMISSION_FAILED


def data_builder (equipment_data):
    global main_menu,sub_menu,sub_sub_menu
    main_menu = []
    sub_menu = []
    sub_sub_menu = [[],[],[],[]]

    i = 0
    for key in equipment_data:
        main_menu.append(key)
        sub_menu.append([])
        for sub_key in equipment_data[key]:
            if(key == 'armors'):
                sub_menu[i].append(sub_key+' - VA: '+str(equipment_data[key][sub_key]['VA'])+' - Cr '+str(equipment_data[key][sub_key]['price']))
            elif (key == 'weapon'):
                pass
            else :
                sub_menu[i].append(sub_key+' - Cr '+str(equipment_data[key][sub_key]))
        i+=1
    j = 0
    for weapon_category in equipment_data["weapon"]:
        for weapon in equipment_data["weapon"][weapon_category]:
            sub_sub_menu[j].append(weapon+' - Cr '+str(equipment_data["weapon"][weapon_category][weapon]))
        j+=1

def main_menu_keyboard_builder ():
    global main_menu
    keyboard = []
    for key in main_menu:
        keyboard.append([f"{key}"])

    keyboard.append(['EXIT'])
    reply_markup =  ReplyKeyboardMarkup(keyboard, on_time_keyboard=True)
    return reply_markup

def sub_menu_keyboard_builder (main_key):
    global main_menu,sub_menu
    sub_menu_index = main_menu.index(main_key)
    keyboard = []
    for key in sub_menu[sub_menu_index]:
        keyboard.append([f"{key}"])

    keyboard.append(['<- GO BACK'])
    reply_markup =  ReplyKeyboardMarkup(keyboard, on_time_keyboard=True)
    return reply_markup

def sub_sub_menu_keyboard_builder (weapon_key):
    global sub_menu,sub_sub_menu
    sub_sub_menu_index = sub_menu.index(weapon_key)
    keyboard = []
    for key in sub_sub_menu[sub_sub_menu_index]:
        keyboard.append([f"{key}"])

    keyboard.append(['<- GO BACK'])
    reply_markup =  ReplyKeyboardMarkup(keyboard, on_time_keyboard=True)
    return reply_markup

# ask user for optinal equipment
def buy_equipment (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    global tmp_user_data

    user_credits = tmp_user_data[f"{user_id}"]["tmp_character"]["credits"]

    with open(f"json_files/equipment.json", "r") as fp:
        equipment_data = json.load(fp)

    data_builder(equipment_data)
    update.message.reply_text(
        '(crediti disponibili: '+str(user_credits)+')\nScegli la categoria: ',
        reply_markup = main_menu_keyboard_builder() 
    )
    return EQUIPMENT_CATEGORY

def equipment_category (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    selected_equipment_category = update.message.text
    global tmp_user_data

    user_credits = tmp_user_data[f"{user_id}"]["tmp_character"]["credits"]

    if selected_equipment_category == 'EXIT':
        update.message.reply_text(
            'Sei di razza aliena? ',
            reply_markup = ReplyKeyboardMarkup(
                [['SI'],['NO']],
                one_time_keyboard=True
            ) 
        )
        return ALIEN_CHOICE

    if selected_equipment_category == 'weapon':
        update.message.reply_text(
            '(crediti disponibili: '+str(user_credits)+')\nSeleziona categoria: ',
            reply_markup = sub_menu_keyboard_builder(selected_equipment_category) 
        )
        return WEAPON_MENU
    update.message.reply_text(
        '(crediti disponibili: '+str(user_credits)+')\nScegli item: ',
        reply_markup = sub_menu_keyboard_builder(selected_equipment_category) 
    )
    return BUY_ITEM

def weapon_menu (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    selected_equipment_category = update.message.text

    global tmp_user_data

    user_credits = tmp_user_data[f"{user_id}"]["tmp_character"]["credits"]
    
    if selected_equipment_category == '<- GO BACK':
        update.message.reply_text(
            '(crediti disponibili: '+str(user_credits)+')\nSeleziona categoria: ',
            reply_markup = main_menu_keyboard_builder() 
        )
        return EQUIPMENT_CATEGORY
    update.message.reply_text(
        '(crediti disponibili: '+str(user_credits)+')\nScegli item: ',
        reply_markup = sub_sub_menu_keyboard_builder(selected_equipment_category) 
    )
    return BUY_ITEM

def buy_item (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    item = update.message.text

    global tmp_user_data

    user_credits = tmp_user_data[f"{user_id}"]["tmp_character"]["credits"]

    if item == '<- GO BACK':
        update.message.reply_text(
            '(crediti disponibili: '+str(user_credits)+')\nSeleziona categoria: ',
            reply_markup = main_menu_keyboard_builder() 
        )
        return EQUIPMENT_CATEGORY
    
    item_price = 0
    match = re.findall(r'(\d+)', item)
    if match:
        item_price = int(match[-1])

    if item_price > user_credits:
        update.message.reply_text(
            'Crediti insufficienti! (crediti disponibili: '+str(user_credits)+')\nSeleziona categoria: ',
            reply_markup = main_menu_keyboard_builder() 
        )
        return EQUIPMENT_CATEGORY
    
    tmp_user_data[f"{user_id}"]["tmp_character"]["credits"] -= item_price

    user_credits = tmp_user_data[f"{user_id}"]["tmp_character"]["credits"]
    pattern = r"(.+) - VA: (\d+) - Cr (\d+)"
    match = re.match(pattern, item)
    if match:
        tmp_user_data[f"{user_id}"]["tmp_character"]["injuries"]["armor"] = match.group(1)
        tmp_user_data[f"{user_id}"]["tmp_character"]["injuries"]["VA"] = int(match.group(2))
    else:
        item_name = item.split('-')[0].strip()
        tmp_user_data[f"{user_id}"]["tmp_character"]["equipment"].append(item_name)

    update.message.reply_text(
        'Equipaggiamento acquistato!\n(crediti disponibili: '+str(user_credits)+')\nSeleziona categoria: ',
        reply_markup = main_menu_keyboard_builder() 
    )
    return EQUIPMENT_CATEGORY

def alien_choice (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    user_choice = update.message.text

    global tmp_user_data

    if user_choice == 'SI':
        keyboard = []
        with open(f"json_files/alien_races.json", "r") as fp:
            alien_races = json.load(fp)
        for race in alien_races.keys():
            keyboard.append([race])
        update.message.reply_text(
            'Seleziona la razza aliena del tuo personaggio, ognuna di esse ha differenti tratti distintivi che verranno aggiunti al tuo personaggio: ',
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True) 
        )
        return TRAITS
    else:
        tmp_user_data[f"{user_id}"]["tmp_character"]["race"] = 'Human'
        update.message.reply_text(
            'Hai terminato la creazione del personaggio!\nPremi il bottone per salvare e terminare',
            reply_markup = ReplyKeyboardMarkup([['SALVA E TERMINA']], one_time_keyboard=True) 
        )
        return SAVE
    
def traits (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    race = update.message.text

    global tmp_user_data

    tmp_user_data[f"{user_id}"]["tmp_character"]["race"] = race
    with open(f"json_files/alien_races.json", "r") as fp:
        race_traits = json.load(fp)[race]

    message_string = 'I seguenti tratti sono stati annotati:\n'
    for trait in race_traits.keys():
        message_string += '- '+trait+'\n'
        tmp_user_data[f"{user_id}"]["tmp_character"]["traits"].append(trait)

    update.message.reply_text(
        message_string+'\nHai terminato la creazione del personaggio!\nPremi il bottone per salvare e terminare',
        reply_markup = ReplyKeyboardMarkup([['SALVA E TERMINA']], one_time_keyboard=True) 
    )
    return SAVE

def save (update: Update, context: CallbackContext):
    user_id = update.effective_user.name

    global tmp_user_data

    str_FOR = str(hex(tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]["FOR"]["value"])[2:]).upper()
    str_DES = str(hex(tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]["DES"]["value"])[2:]).upper()
    str_RES = str(hex(tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]["RES"]["value"])[2:]).upper()
    str_INT = str(hex(tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]["INT"]["value"])[2:]).upper()
    str_EDU = str(hex(tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]["EDU"]["value"])[2:]).upper()
    str_SOC = str(hex(tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]["SOC"]["value"])[2:]).upper()

    tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]["PPU"] = str_FOR+str_DES+str_RES+str_INT+str_EDU+str_SOC
    if os.path.isfile(f"json_files/users/{user_id}.json"):
        with open(f"json_files/users/{user_id}.json", "r") as fp:
            user_info = json.load(fp)
    else:
        user_info = {}

    character_name_key = ("_".join(tmp_user_data[f'{user_id}']['tmp_character']['name'].split())).lower()
    user_info[f"{character_name_key}"] = tmp_user_data[f"{user_id}"]["tmp_character"]

    with open(f"json_files/users/{user_id}.json", "w") as fp:
        json.dump(user_info, fp, indent=4)

    tmp_user_data.pop(f"{user_id}")
    update.message.reply_text(
        'Creazione personaggio completata! \nPuoi creare un nuovo personaggio con i comando /create oppure usare il comando /show per vedere i personaggi creati.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def show (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    keyboard = []
    if os.path.isfile(f"json_files/users/{user_id}.json"):
        with open(f"json_files/users/{user_id}.json", "r") as fp:
            user_characters = json.load(fp)
    else:
        user_characters = {}
    try:
        characters_list = [*user_characters]
        for name in characters_list:
            keyboard.append([f"{name}"])
        update.message.reply_text("Lista dei personaggi di "+str(user_id),reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return 0
    except KeyError:
        update.message.reply_text("Non hai ancora creato nessun personaggio!")
        return ConversationHandler.END

def format_player_sheet(user_data):
    formatted_message = ""
    formatted_message += f"Name: {user_data['name']}\n"
    formatted_message += f"Race: {user_data['race']}\n"
    formatted_message += f"Gender: {user_data['gender']}\n"
    formatted_message += f"Age: {user_data['age']}\n"
    formatted_message += f"Origin: {user_data['origin']}\n"
    formatted_message += f"Description: {user_data['description']}\n"
    formatted_message += f"Traits: {', '.join(user_data['traits'])}\n\n"
    formatted_message += "Characteristics:\n"
    for characteristic, values in user_data['characteristics'].items():
        if characteristic == 'PPU':
            formatted_message += f"{characteristic}: {values}\n\n"
        else:
            formatted_message += f"{characteristic}: {values['value']} ({'+' if values['modifier'] >= 0 else ''}{values['modifier']})\n"
    formatted_message += "Injuries:\n"
    formatted_message += f"FOR: {user_data['injuries']['FOR']}\n"
    formatted_message += f"DES: {user_data['injuries']['DES']}\n"
    formatted_message += f"RES: {user_data['injuries']['RES']}\n"
    formatted_message += f"Armor: {user_data['injuries']['armor']}\n"
    formatted_message += f"VA: {user_data['injuries']['VA']}\n\n"
    formatted_message += "Abilities:\n"
    for ability, level in user_data['abilities'].items():
        formatted_message += f"{ability}: {level}\n"
    formatted_message += f"Goods: {', '.join(user_data['goods'])}\n"
    formatted_message += f"Credits: {user_data['credits']}\n\n"
    formatted_message += "Careers:\n"
    for i in range(1, 8):
        career_data = user_data['careers'][str(i)]
        if career_data['name'] == '':
            continue
        formatted_message += f"Career {i}: {career_data['name']}\n"
        formatted_message += f"Grade: {career_data['grade']}\n"
        formatted_message += f"Conscription Flag: {career_data['conscription_flag']}\n"
        formatted_message += f"Service Periods: {career_data['service_periods']}\n\n"

    return formatted_message

def get_player_sheet(update: Update, context: CallbackContext):

    charcter_name = update.message.text

    user_id = update.effective_user.name

    with open(f"json_files/users/{user_id}.json", "r") as fp:
        try:
            user_data = json.load(fp)[f"{charcter_name}"]
            update.message.reply_text(format_player_sheet(user_data))
            return ConversationHandler.END
        except KeyError:
            update.message.reply_text(f"You have no character named {charcter_name}!")
            return ConversationHandler.END
        
# Unknown commands
def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Unknown command, try /help')


if __name__ == '__main__':
    main()
