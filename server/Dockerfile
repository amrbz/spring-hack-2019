FROM ubuntu:xenial

WORKDIR /opt
RUN apt-get update
RUN apt-get install -y tar git curl nano wget
RUN apt-get install -y build-essential libssl-dev libffi-dev python-dev
RUN apt-get install -y python3-pip python3-setuptools
RUN apt-get update

RUN mkdir /tmp/Python3.7
WORKDIR /tmp/Python3.7
RUN wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tar.xz
RUN tar xvf Python-3.7.2.tar.xz

WORKDIR /tmp/Python3.7/Python-3.7.2
RUN ./configure --enable-optimizations
RUN make altinstall

RUN mkdir /root/.data
RUN mkdir /root/.data/leveldb
RUN mkdir /root/.data/leveldb/messenger
RUN mkdir /root/.data/leveldb/sql

WORKDIR /opt
COPY requirements.txt /opt/requirements.txt
RUN pip3.7 install -r requirements.txt

COPY api /opt/api
COPY files /opt/files
COPY config.stage.ini /opt/config.ini
COPY server.py /opt/server.py

EXPOSE 8080
