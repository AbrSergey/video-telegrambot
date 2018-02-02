FROM ubuntu:16.04
RUN apt-get -y update
RUN apt-get install -y python3 && apt-get install -y python3-pip
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:mc3man/trusty-media
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 8E51A6D660CD88D67D65221D90BD7EACED8E640A
RUN apt-get install -y ffmpeg
RUN apt-get -y install rabbitmq-server
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip3 install -r requirements.txt
ADD . /code/