#!/usr/bin/env python3

import pika
import json
import speech_recognition as sr
from urllib.parse import urlparse
import validators
import pafy
import wave
import contextlib
import subprocess
import hashlib
import glob
import requests

from config import TOKEN, BING_KEY

url_bot = "https://api.telegram.org/bot" + TOKEN + "/"


def get_id(url):
    url = url[url.find("=")+1:]
    if url.find("=") == -1:
        url = url[:url.find("=")]
    return url


def clean_text(text):
    words = text.split(" ")
    text = ""
    for word in words:
        if word != "hmm" and word != "Hmm":
            text += word + " "
    return text


def lang_check(l):
    if l in ['en', 'EN', 'eng', 'english', 'ENG']:
        return 'en-US'
    else:
        return "ru-RU"


def sub_check(s):
    if s == "no_sub":
        return False
    else:
        return True


def sound_from_youtube(url):
    video = pafy.new(url)
    best = video.getbest(preftype="webm")
    name = get_id(url)
    best.download(filepath=name + ".webm")
    command = "ffmpeg -i " + name + ".webm -ab 160k -ac 2 -ar 44100 -vn " + name + ".wav"
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


def send_mess(chat, text):
    params = {'chat_id': chat, 'text': text}
    response = requests.post(url_bot + 'sendMessage', data=params)
    if response.ok == False:
        print(response)
    return response


def download_subtitles(url):
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


def send_subtitles(chat_id, message):
    message = message.split(" ")
    url = message[0]
    lang = "ru-RU"
    sub = True
    name = get_id(url)
    name_hashed = hashlib.sha1(name.encode('utf8')).hexdigest()
    if len(message) == 2:
        lang = lang_check(message[1])
        sub = sub_check(message[1])
    if len(message) == 3:
        lang = lang_check(message[1])
        sub = sub_check(message[2])
    if sub and check_in_folder(name):
        with open('subtitles/' + name_hashed) as f:
            fulltext = f.readlines()
            i = 0
            text = ''
            for line in fulltext:
                text = text + line
                i = i + 1
                if i % 5== 0:
                    send_mess(chat_id, text)
                    text = ''
            send_mess(chat_id, text)
            send_mess(chat_id, text="*** Subtitles are over  ***")
            print("Subtitles are over  " + str(chat_id)) #TMP
    elif sub and download_subtitles(url):
        with open('subtitles/' + name_hashed) as f:
            fulltext = f.readlines()
            i = 0
            text = ''
            for line in fulltext:
                text = text + line
                i = i + 1
                if i % 5== 0:
                    send_mess(chat_id, text)
                    text = ''
            send_mess(chat_id, text)
            send_mess(chat_id, text="*** Subtitles are over  ***")
            print("Subtitles are over  " + str(chat_id)) #TMP
    else:
        send_mess(chat_id, text="*** Good URL. Wait for the audio file loading ***")
        sound_from_youtube(url)
        send_mess(chat_id, text="*** Audio file is loaded. Now messages with subtitles will come to you ***")
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
                    text = (r.recognize_bing(audio, key=BING_KEY, language=lang)) + "\n"
                    text = clean_text(text)
                    fulltext.append(text)
                except sr.UnknownValueError:
                    text = "*** Microsoft Bing Voice Recognition could not understand this fragment ***\n"
                except sr.RequestError as e:
                    text = "*** Could not request results from Microsoft Bing Voice Recognition service ***\n"
                send_mess(chat_id, text=text)
                duration -= 15
        send_mess(chat_id, text="*** Subtitles are over ***")
        with open('subtitles/' + name_hashed, "w") as f:
            for line in fulltext:
                if len(line) > 2 and not line[2] == ':' and not line[0:2] == '\n':
                    f.writelines(line)
        subprocess.call(["rm", name + ".wav"])
        subprocess.call(["rm", name + ".webm"])


def callback(ch, method, properties, body):
    parsed_json = json.loads(body.decode('utf-8'))
    chat_id = parsed_json["chat_id"]
    url = parsed_json["url"]

    if send_mess(chat_id, text="***  There is subtitles for this video: ***").ok == True: #TMP
        print("Message is send") #TMP
    else: #TMP
        print("Message is NOT send") #TMP

    send_subtitles(chat_id, url)


# def main():
queue = 'telegram_bot'
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue=queue, durable=True, auto_delete=False, exclusive=False)
channel.basic_consume(callback, queue=queue, no_ack=True)
channel.start_consuming()
print("Worker...")

# if __name__ == '__main__':
#     main()