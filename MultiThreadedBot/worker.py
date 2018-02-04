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
import requests
from youtube_dl import YoutubeDL
import re
import time


from config import TOKEN, BING_KEY

REGULAR_EXPRESSION = '<[a-zA-Z0-9|\.]*>|<\/c>|<[0-9:.]*>'
url_bot = "https://api.telegram.org/bot" + TOKEN + "/"
TIME_SLEEP = 2 #dream between sending messages, else ERROR 429
COUNT_STR = 20


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
    best.download(filepath='tmp/' + name + ".webm")
    command = "ffmpeg -i " + 'tmp/' + name + ".webm -ab 160k -ac 2 -ar 44100 -vn " + 'tmp/' + name + ".wav"
    subprocess.call(command, shell=True)


def url_check(url):
    list = ['www.youtube.', 'www.youtube.com']
    if re.search("youtu.be", url) != None:
        url = url.replace("youtu.be/", "www.youtube.com/watch?v=")
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
    if text == '':
        return True
    else:
        params = {'chat_id': chat, 'text': text}
        response = requests.post(url_bot + 'sendMessage', data=params)
        req_code = response.content
        req_code = json.loads(req_code.decode('utf-8'))
        if req_code["ok"] == False:
            print(response.ok)
            print(req_code["description"])
            return False
        else:
            time.sleep(TIME_SLEEP)
            return True


def download_subtitles(url, lang):
    try:
        id = get_id(url)
        id_hash = hashlib.sha1(id.encode('utf8')).hexdigest()
        ydl = YoutubeDL(dict(allsubtitles=True, writeautomaticsub=True))
        with ydl:
            result = ydl.extract_info(url, download=False)
        url_sub = result['requested_subtitles'][lang[:2]]['url']
        response = requests.get(url_sub)
        text = response.text

        parser = re.search(REGULAR_EXPRESSION, text)
        while parser != None:
            parser = parser.group(0)
            text = text.replace(parser, '')
            parser = re.search(REGULAR_EXPRESSION, text)

        f_write = open('tmp/' + id_hash, 'w')
        f_write.write(text)
        f_write.close()

        try:
            with open('tmp/' + id_hash, 'r') as f:
                file_sub = open('subtitles/' + id_hash, 'w')
                i = 0
                text = ''
                for line in f:
                    if i < 5:
                        if re.search('-->|{|}|::|##|WEBVTT|Language:|Kind:|Style:', line) == None:
                            text = text + line
                            text = text.replace("\n", " ")
                            text = text.replace("  ", " ")
                            i = i + 1
                    else:
                        i = 0
                        text = text + "\n"
                        file_sub.writelines(text)
                        text = ''
            file_sub.close()
            subprocess.call(["rm", 'tmp/' + id_hash])
            return True
        except Exception:
            return False
    except:
        return False


def send_subtitles(chat_id, message):
    print("In send_subtitles")
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
                if i % COUNT_STR == 0:
                    send_mess(chat_id, text)
                    text = ''
            send_mess(chat_id, text)
            send_mess(chat_id, text="*** Subtitles are over  ***")
    elif sub and download_subtitles(url, lang):
        with open('subtitles/' + name_hashed) as f:
            fulltext = f.readlines()
            i = 0
            text = ''
            for line in fulltext:
                text = text + line
                i = i + 1
                if i % COUNT_STR == 0:
                    send_mess(chat_id, text)
                    text = ''
            send_mess(chat_id, text)
            send_mess(chat_id, text="*** Subtitles are over  ***")
    else:
        send_mess(chat_id, text="*** Good URL. Wait for the audio file loading ***")
        try:
            try:
                sound_from_youtube(url)
                send_mess(chat_id, text="*** Audio file is loaded. Now messages with subtitles will come to you ***")
                r = sr.Recognizer()
                with contextlib.closing(wave.open('tmp/' + name + ".wav", 'r')) as f:
                    frames = f.getnframes()
                    rate = f.getframerate()
                    duration = frames / float(rate)
                fulltext = []
                with sr.AudioFile('tmp/' + name + ".wav") as source:
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
                subprocess.call(["rm", 'tmp/' + name + ".wav"])
                subprocess.call(["rm", 'tmp/' + name + ".webm"])
            except Exception:
                send_mess(chat_id, text="*** Can't download audiofile ***")
        except:
            send_mess(chat_id, text="*** Error!!! Check the URL ***")


def callback(ch, method, properties, body):
    try:
        parsed_json = json.loads(body.decode('utf-8'))
        chat_id = parsed_json["chat_id"]
        url = parsed_json["url"]
        send_subtitles(chat_id, url)
    except:
        pass


def main():
    queue = 'telegram_bot'
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue)  # , durable=True, auto_delete=False, exclusive=False)
    channel.basic_consume(callback, queue=queue, no_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    main()