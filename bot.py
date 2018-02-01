from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import speech_recognition as sr
from urllib.parse import urlparse
import validators
import pafy
import wave
import contextlib
import subprocess
import hashlib
import glob


"""   Bot part   """


from config import TOKEN, BING_KEY


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Good day, " + update.message.chat.first_name + "! I am the videosubtitler bot")
    bot.send_message(chat_id=update.message.chat_id,
                     text="To know more information about me write command 'help'")


def echo(bot, update):
    message = update.message.text
    if url_check(message):
        name = get_id(message)
        name_hashed = hashlib.sha1(name.encode('utf8')).hexdigest()
        if check_in_folder(name):
            with open('subtitles/' + name_hashed) as f:
                fulltext = f.read()
                bot.send_message(chat_id=update.message.chat_id, text="*** Good URL. "
                                                                      "There is subtitles for this video: ***")
                bot.send_message(chat_id=update.message.chat_id, text=fulltext)
        elif get_subtitles(message):
            with open('subtitles/' + name_hashed) as f:
                fulltext = f.read()
                bot.send_message(chat_id=update.message.chat_id, text="*** Good URL. "
                                                                      "There is subtitles for this video: *** ")
                bot.send_message(chat_id=update.message.chat_id, text=fulltext)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="*** Good URL. Wait for the audio file loading ***")
            sound_from_youtube(message)
            bot.send_message(chat_id=update.message.chat_id, text="*** Audio file is loaded. "
                                                                  "Now messages with subtitles will come to you ***")
            r = sr.Recognizer()
            with contextlib.closing(wave.open(name + ".wav", 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
            fulltext = []
            with sr.AudioFile(name + ".wav") as source:
                while True:
                    if duration < 0:
                        break
                    audio = r.record(source, duration=15)
                    try:
                        text = (r.recognize_bing(audio, key=BING_KEY, language="ru-RU")) + "\n"
                    except sr.UnknownValueError:
                        text = "*** Microsoft Bing Voice Recognition could not understand this fragment ***\n"
                    except sr.RequestError as e:
                        text = "*** Could not request results from Microsoft Bing Voice Recognition service ***\n"
                    bot.send_message(chat_id=update.message.chat_id, text=text)
                    fulltext.append(text)
                    duration -= 15
            bot.send_message(chat_id=update.message.chat_id, text="*** Subtitles are over ***")
            with open('subtitles/' + name_hashed, "w") as f:
                for line in fulltext:
                    if len(line) > 2 and not line[2] == ':' and not line[0:2] == '\n':
                        f.writelines(line)
            subprocess.call(["rm", name + ".wav"])
            subprocess.call(["rm", name + ".webm"])
    else:
        bot.send_message(chat_id=update.message.chat_id, text="*** This is no valid URL. " +
                                                              "Please enter correct YouTube video URL ***")


def help(bot, update):
    help_text = ""
    with open("help.txt", "r") as h:
        for s in h:
            help_text += "\n" + s
    bot.send_message(chat_id=update.message.chat_id, text=help_text)


updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)
echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)
help_handler = CommandHandler("help", help)
dispatcher.add_handler(help_handler)
updater.start_polling()


"""   Service functions   """


def get_id(url):
    url = url[url.find("=")+1:]
    if url.find("=") == -1:
        url = url[:url.find("=")]
    return url


def sound_from_youtube(url):
    video = pafy.new(url)
    best = video.getbest(preftype="webm")
    name = get_id(url)
    best.download(filepath=name + ".webm")
    command = "ffmpeg -i " + name + ".webm -ab 160k -ac 2 -ar 44100 -vn " + name + ".wav"
    # command = "ffmpeg -i " + name + ".webm " + name + ".wav"
    subprocess.call(command, shell=True)


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


def check_in_folder(id):
    id_hash = hashlib.sha1(id.encode('utf8')).hexdigest()
    try:
        open('subtitles/' + id_hash)
        return True
    except IOError:
        return False


def get_subtitles(url):
    id = get_id(url)
    id_hash = hashlib.sha1(id.encode('utf8')).hexdigest()
    subprocess.call(["youtube-dl", "--write-sub", "--skip-download", "--output", id_hash, url])
    try:
        filename_tmp = glob.glob(id_hash + '*')
        assert (len(filename_tmp) == 1)
        with open(filename_tmp[0], 'r') as f:
            file_sub = open('subtitles/' + id_hash, 'w')
            for line in f:
                if len(line) > 2 and not line[2] == ':' and not line[0:2] == '\n':
                    file_sub.writelines(line)
        f.close()
        subprocess.call(["rm", filename_tmp[0]])
        return True
    except Exception:
        return False
