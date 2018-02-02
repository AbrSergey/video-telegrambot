#!/usr/bin/env python3

import pika
import json
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from urllib.parse import urlparse
import validators

from config import TOKEN, BING_KEY



def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Good day, " + update.message.chat.first_name + "! I am the videosubtitler bot")
    bot.send_message(chat_id=update.message.chat_id,
                     text="To know more information about me write command 'help'")

def echo(bot, update):
    message = update.message.text
    chat_id = update['message']['chat']['id']
    if url_check(message):
        print("before json") #TMP
        json_data = json.dumps({"chat_id" : chat_id, "url" : message})
        print("before send" + json_data) #TMP
        bot.send_message(chat_id=update.message.chat_id, text="*** Good URL ***")
        channel.basic_publish(exchange='',
                              routing_key=queue,
                              body=json_data,
                              properties=pika.BasicProperties(delivery_mode=2))
        print("after send") #TMP
    else:
        print("Error url") #TMP
        bot.send_message(chat_id=update.message.chat_id, text="*** This is no valid URL. " +
                                                              "Please enter correct YouTube video URL ***")

def help(bot, update):
    help_text = ""
    with open("help.txt", "r") as h:
        for s in h:
            help_text += "\n" + s
    bot.send_message(chat_id=update.message.chat_id, text=help_text)

def url_check(url):
    list = ['www.youtube.']
    if validators.url(url):
        url_netloc = urlparse(url).netloc
        for i in list:
            if not url_netloc.find(i) == 0:
                return False
        return True
    else:
        return False


def main():

    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)
    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)
    help_handler = CommandHandler("help", help)
    dispatcher.add_handler(help_handler)
    updater.start_polling()

if __name__ == '__main__':
    queue = 'telegram_bot'
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True, auto_delete=False, exclusive=False)
    main()