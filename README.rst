=================
video-telegrambot
=================

Video-telegrambot - это бот для мессенджера Telegram, который умеет находить и создавать субтитры к видео с Youtube. Есть версия, поддерживающая многопоточность с помощью RabbitMQ.

---------
Установка
---------

Однопоточный бот: ::

    Загрузите файлы из директории OneTheadedBot и введите следующие комманды:

    apt install -y software-properties-common
    add-apt-repository ppa:mc3man/trusty-media
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 8E51A6D660CD88D67D65221D90BD7EACED8E640A
    apt-get install -y ffmpeg
    pip3 install -r requirements.txt

    Добавьте файл congif.py с полями TOKEN="your telegram bot token" и BING_KEY="your microsoft bing speech token"

    pip3 ./bot.py

Многопоточный бот: ::

    Загрузите файлы из директории MultiThreadedBot и введите следующие комманды:

    apt install -y software-properties-common
    add-apt-repository ppa:mc3man/trusty-media
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 8E51A6D660CD88D67D65221D90BD7EACED8E640A
    apt-get install -y ffmpeg
    apt-get -y install rabbitmq-server
    pip3 install -r requirements.txt
    rabbitmq-server start

    Добавьте файл congif.py с полями TOKEN="your telegram bot token" и BING_KEY="your microsoft bing speech token"

    python3 ./reader.py
    python3 ./worker.py
    ...
    python3 ./worker.py

Второй вариант - использование docker-контейнера: ::

    Скачайте и установите Docker и загрузите образ с помощью команды:
    
    docker pull alekseypauls/videotelegrambot
    
    или 
    
    docker pull alekseypauls/multithreadedbot
    
    Сойздайте контейнер:
    
    docker run -it -p 80:80 alekseypauls/videotelegrambot bash
    
    Внутри контейнера выполните команды:
    
    export LANGUAGE=ru_RU.UTF-8
    export LC_CTYPE=ru_RU.UTF-8
    export LC_NUMERIC=ru_RU.UTF-8
    export LC_TIME=ru_RU.UTF-8
    export LC_COLLATE=ru_RU.UTF-8
    export LC_MONETARY=ru_RU.UTF-8
    export LC_MESSAGES=ru_RU.UTF-8
    export LC_PAPER=ru_RU.UTF-8
    export LC_NAME=ru_RU.UTF-8
    export LC_ADDRESS=ru_RU.UTF-8
    export LC_TELEPHONE=ru_RU.UTF-8
    export LC_MEASUREMENT=ru_RU.UTF-8
    export LC_IDENTIFICATION=ru_RU.UTF-8
    export LC_ALL=ru_RU.UTF-8
    python3 ./bot.py
    
    Готово! 

--------------------------
Пользовательский интерфейс
--------------------------

Бот поддерживает команды **/start** и **/help**. Чтобы получить субтитры, вы должны отправить боту корректный URL видео. Используйте необязательный параметр **en** (**EN**, **eng**, **english**), чтобы распознавать английскую речь, и необязательный параметр **no_sub**, чтобы распознавать аудио, игнорируя сохраненные субтитры или субтитры с Youtube.
