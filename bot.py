import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# temporary user info during creation
tmp_user_data = {}

# Funzione per gestire il comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invia un messaggio di benvenuto quando il comando /start viene inviato."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Ciao! Sono un bot che ti aiuterà a creare un personaggio per Cepheus Engine RPG. Iniziamo!')

# Funzione per gestire il comando /help
async def help_f(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Messaggio di aiuto"""
    await context.bot.send_message(chat_id=update.effective_chat.id,text="La lista dei comandi disponibili è presente nella tua tastiera")
    
# Funzione per gestire comandi sconosciti
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Messaggio di errore per comandi sconosciuti"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Unknown command, try /help')

# Funzione per gestire messaggi diretti
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde ai messaggi"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Unknown command, try /help')


if __name__ == '__main__':
    application = ApplicationBuilder().token('6156862079:AAEV4XPTc5YF3CJJYNRoEeg6-_gkVTN-M-o').build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    help_handler = CommandHandler('help', help_f)
    application.add_handler(help_handler)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)
    
    application.run_polling()