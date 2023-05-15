import configparser
import logging
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

PROCESS, TITLE, NAME = range(3)


def get_by_title(anime_title):
    quote = requests.get('https://animechan.vercel.app/api/random/anime', params={'title': anime_title})
    if quote.status_code == 200:
        quote = quote.json()
        return quote['quote'], quote['character']
    return None


def get_by_name(character_name):
    quote = requests.get('https://animechan.vercel.app/api/random/character', params={'name': character_name})
    if quote.status_code == 200:
        quote = quote.json()
        return quote['quote'], quote['anime']
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['Anime Title', 'Character Name', '/cancel']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text('Lets choose something', reply_markup=markup_key)
    return PROCESS


async def process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    reply_keyboard = [['/cancel']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    if answer == 'Anime Title':
        await update.message.reply_html(f'<i><b>Send me the title.</b></i>', reply_markup=markup_key)
        return TITLE
    await update.message.reply_html(f'<i><b>Send me the name.</b></i>', reply_markup=markup_key)
    return NAME


async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    anime_title = update.message.text
    character_quote = get_by_title(anime_title)
    if character_quote is not None:
        await update.message.reply_html(f'<b>{character_quote[0]}</b>\n\n<i>{character_quote[1]}</i>',
                                        reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_html(f'<i><b>Something went wrong</b></i>', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    character_quote = get_by_name(name)
    if character_quote is not None:
        await update.message.reply_html(f'<b>{character_quote[0]}</b>\n\n<i>{character_quote[1]}</i>',
                                        reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_html(f'<i><b>Something went wrong</b></i>', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = update.message.from_user
    await update.message.reply_html('Lets try again!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    application = ApplicationBuilder().token(config['bot']['token']).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PROCESS: [MessageHandler(filters.Regex('^(Anime Title|Character Name)$'), process)],
            TITLE: [MessageHandler(filters.TEXT^filters.COMMAND, get_title)],
            NAME: [MessageHandler(filters.TEXT^filters.COMMAND, get_name)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)
    application.run_polling()
