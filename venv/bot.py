import re
import random
import json

##bot part
#from token_conf import TOKEN

TOKEN="528722105:AAFoq0qJFgwLEf6_hgm6MFUtLl0zwth2nOM"

from telegram.ext import Updater

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Good day! I am the simply bot")


from telegram.ext import CommandHandler

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def echo(bot, update):
    text = update.message.text
    bot.send_message(chat_id=update.message.chat_id, text='It is answer')


from telegram.ext import MessageHandler, Filters

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)


def sayhello(bot, update, args):
    result = 'Hello!'
    bot.send_message(chat_id=update.message.chat_id, text=result)


sayhello_handler = CommandHandler('sayhello', sayhello, pass_args=True)
dispatcher.add_handler(sayhello_handler)

updater.start_polling()