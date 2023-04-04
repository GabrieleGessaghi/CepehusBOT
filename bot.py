import json
import logging
import dyce_roll as dyce
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, ConversationHandler, Filters

# character creation stages
GENDER, AGE, ORIGIN, RACE, TRAITS, CHARACTERISTICS, ABILITIES1, ABILITIES2, FIRST_CAREER = range(9)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# temporary user info during creation
tmp_user_data = {}
ability_counter = 3
ability_list = ['Amministrazione','Avvocato','Animali','Baldoria',
                    'Comunicazioni','Computer','Elettronica','Ingegneria',
                    'Scienze Biologiche','Lingue','Meccanica','Medicina',
                    'Scienze Fisiche','Scienze Sociali','Scienze Spaziali']

# Funzione per gestire il comando /start
def start(update: Update, context: CallbackContext):
    """Invia un messaggio di benvenuto quando il comando /start viene inviato."""
    context.bot.send_message(chat_id=update.effective_chat.id, text='Ciao! Sono un bot che ti aiuterà a creare un personaggio per Cepheus Engine RPG. Iniziamo!')

# Funzione per gestire il comando /help
def help_f(update: Update, context: CallbackContext):
    """Messaggio di aiuto"""
    context.bot.send_message(chat_id=update.effective_chat.id,text="La lista dei comandi disponibili è presente nella tua tastiera")
    
# Funzione per gestire comandi sconosciti
def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Unknown command, try /help')

# Funzione per gestire messaggi diretti
def echo(update: Update, context: CallbackContext):
    """Risponde ai messaggi"""
    context.bot.send_message(chat_id=update.effective_chat.id, text='Unknown command, try /help')

def cancel(update: Update, context: CallbackContext):

    user_id = update.effective_user.name
    global tmp_user_data

    try:
        del(tmp_user_data[f"{user_id}"])
    except KeyError:
        pass
    update.message.reply_text('Creazione personaggio interrotta!', reply_markup=ReplyKeyboardRemove)

    return ConversationHandler.END

def create_character(update: Update, context: CallbackContext):
    """Processo di creazione del personaggio"""
    update.message.reply_text('Iniziamo a creare il personaggio, per prima cosa dagli un nome:')
    return GENDER

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

    update.message.reply_text(
        'Ottimo, seleziona il genere del tuo personaggio:',
        reply_markup= ReplyKeyboardMarkup(
            [['Uomo'], ['Donna']],
            on_time_keyboard= True, 
            input_field_placeholder='Seleziona il genere'
            )
        )
    return AGE

def set_age(update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    character_gender = update.message.text
    with open(f"json_files/character_sheet.json", "r") as fp:
        new_character = json.load(fp)
    
    new_character['gender'] = character_gender
    update.message.reply_text("Quanti anni ha il tuo personaggio ?")

    return ORIGIN


def set_origin(update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    character_age = update.message.text

    with open(f"json_files/character_sheet.json", "r") as fp:
        new_character = json.load(fp)

    new_character['age'] = character_age

    update.message.reply_text("Da dove proviene il tuo persoanggio (pianeta di origine)?")
    return CHARACTERISTICS

def calculate_characteristics (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    character_origin = update.message.text

    with open(f"json_files/character_sheet.json", "r") as fp:
        new_character = json.load(fp)

    new_character['origin'] = character_origin
    
    update.message.reply_text(
        'Calcoliamo ora le caratteristiche usando 2D6',
        reply_markup= ReplyKeyboardMarkup(
            [['CALCOLA']],
            on_time_keyboard= True
            )
        )

    return ABILITIES1


def select_abilities1 (update: Update, context: CallbackContext):
    
    user_id = update.effective_user.name
    global tmp_user_data

    with open(f"json_files/character_sheet.json", "r") as fp:
        new_character = json.load(fp)

    tmp_user_data[f"{user_id}"] = {}
    tmp_user_data[f"{user_id}"]["tmp_character"] = new_character
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

    for key in tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"]:
        if key == 'PSI' or key == 'PPU' :
            continue
        new_character['characteristics'][key]['value'] = tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][key]["value"] 
        new_character['characteristics'][key]['modifier'] = tmp_user_data[f"{user_id}"]["tmp_character"]["characteristics"][key]["modifier"] 

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

def select_abilities2 (update: Update, context: CallbackContext):
    user_id = update.effective_user.name
    character_ability = update.message.text
    dict_entry = {"{}".format(character_ability):"0"}

    global tmp_user_data
    global ability_counter
    global ability_list

    #tmp_local = tmp_user_data[f"{user_id}"]
    tmp_user_data[f"{user_id}"]['tmp_character']['abilities'].append(dict_entry)
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
    
    update.message.reply_text('abilità aggiunte!')

    return FIRST_CAREER


def select_first_career (update: Update, context: CallbackContext):
    update.message.reply_text('eskereee')

if __name__ == '__main__':
    application = Updater('6156862079:AAHuCvPIhKhwGYomI_W_krkklUhCcot8U_Q', use_context= True)
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

    select_first_career_handler = CommandHandler('first_career', select_first_career)
    bot.add_handler(select_first_career_handler)



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
            FIRST_CAREER: [MessageHandler(Filters.text & ~Filters.command, select_first_career)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    bot.add_handler(character_creation_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    bot.add_handler(unknown_handler)
    
    application.start_polling()
    application.idle()