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
      FIRST_CAREER, START_CAREER, ADMISSION_FAILED, BASIC_TRAIN, SURVIVE, DEAD= range(14)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# temporary user info during creation
tmp_user_data = {}
ability_counter = 3
selected_career = None
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
            SURVIVE: [MessageHandler(Filters.text & ~Filters.command, survival_trial)]
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
    global tmp_user_data
    try:
        del(tmp_user_data[f"{user_id}"])
    except KeyError:
        pass
    update.message.reply_text(
        'Creazione personaggio interrotta!', reply_markup=ReplyKeyboardRemove()
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

    update.message.reply_text("Da dove proviene il tuo persoanggio (pianeta di origine)?")
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
    admission_roll = roll + tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{admission_check_attribute[0]}"]["modifier"]

    result = None

    if admission_roll >= admission_check_value:
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
        update.message.reply_text('Sei stato rifiutato !')
        return START_CAREER

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
    
    
def survival_trial (update: Update, context: CallbackContext):
    user_id = update.effective_user.name

    global tmp_user_data,selected_career
    with open(f"json_files/careers.json", "r") as fp:
        career_survival_check = json.load(fp)[f"{selected_career}"]["survive"]

    survival_check_attribute = list(career_survival_check.keys())
    survival_check_value = career_survival_check[survival_check_attribute[0]]

    roll = dyce.dice_roll(2,6)

    if roll == 2 :
        # TODO dead
        update.message.reply_text('Hai fallito la prova di sopravvivenza perchè hai tirato un 2 naturale! Crea un nuovo personaggio con il comando /create oppure selezioanando dal menu')
    

    result = roll + tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][f"{survival_check_attribute[0]}"]["modifier"]

    if result >= survival_check_value :
        # TODO survived
        update.message.reply_text('Sei sopravvissuto !')
    else:
        # TODO dead
        update.message.reply_text('Hai fallito la prova di sopravvivenza perchè hai tirato un 2 naturale! Crea un nuovo personaggio con il comando /create oppure selezioanando dal menu')
        
    
# Unknown commands
def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Unknown command, try /help')


if __name__ == '__main__':
    main()