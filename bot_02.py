
from io import BytesIO
from queue import Queue
import requests
from typing import Final
from flask import Flask, request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, ContextTypes, Updater, CallbackContext, CallbackQueryHandler, Dispatcher
from bot_01 import search_movies, get_movie
import os

# Define the constants
TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL")
bot = Bot(TOKEN)
BOT_USERNAME: Final = '@JustForFun_04bot'

# Commands
#bot = telebot.TeleBot(TOKEN, parse_mode=None)
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Hello! Thanks for messaging me.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.message.from_user.first_name}! Welcome to Just For Fun Community. Thanks for messaging me. My username is {BOT_USERNAME}")
    await update.message.reply_text("I'm a bot that helps you to interact with JustForFun Channel files.")
    await update.message.reply_text(f"Download For Fun")
    update.message.reply_text(" Enter Movie Name : ")

def find_movie(update, context):
    search_results = update.message.reply_text("Processing...")
    query = update.message.text
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        search_results.edit_text('Sorry, There is no such movie with name in our Database.\nCheck If You Have Misspelled The Movie Name.')

def movie_result(update, context) -> None:
    query = update.callback_query
    s = get_movie(query.data)
    response = requests.get(s["img"])
    img = BytesIO(response.content)
    query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
    link = ""
    links = s["links"]
    for i in links:
        link += "🎬" + i + "\n" + links[i] + "\n\n"
    caption = f" Download Links :-\n\n{link}"
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(text=caption[x:x+4095])
    else:
        query.message.reply_text(text=caption)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please type the file name correctly and if you want any file in specific language then please add the language name too with the file name. \nEx. 'Avatar Hindi' or 'Animal'.")

async def custum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custum command.")

# Handle Logics
# Define a function to handle responses from users
def handle_response(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()

    # Check the user's input and respond accordingly
    if user_input == 'hello':
        update.message.reply_text('Hello! How can I help you today?')
    elif user_input == 'bye':
        update.message.reply_text('Goodbye! Have a great day!')
    else:
        update.message.reply_text('I\'m sorry, I didn\'t understand that. Please try again.')

def contact(update, context):
    update.message.reply_text(
        """
        Admin - @imkritvm
        Channnel - @JustForFunChannel_04
        """
    )

# Define a function to handle the /getfiles command
def get_files(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    messages = context.bot.get_chat_history(chat_id=chat_id, limit=10)  # Change the limit as needed

    for message in messages:
        if message.document:
            file_id = message.document.file_id
            file = context.bot.get_file(file_id)
            file.download('downloaded_files/' + message.document.file_name)  # Save the file to a local directory

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        elif message_type == 'group':
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

def setup():
    print('Starting BOt...')
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue, use_context=True)
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("custum", custum_command))
    dispatcher.add_handler(MessageHandler(Filters.text, find_movie))
    dispatcher.add_handler(CallbackQueryHandler(movie_result))
    dispatcher.add_handler(MessageHandler(Filters.document, get_files))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact))
    dispatcher.add_error_handler(error)

    print('Pollling...')
    app.run_polling(poll_interval=3)
    return dispatcher

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/{}'.format(TOKEN), methods=['GET', 'POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), bot)
    setup().process_update(update)
    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"
