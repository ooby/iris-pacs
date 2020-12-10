FROM ubuntu:focal

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install git python3-dev python3-pip gnupg wget apt-utils -y
RUN pip3 install pip --upgrade
RUN pip3 install pika pydicom pymongo pynetdicom pytest setuptools

ARG TIMEZONE
ENV TZ="${TIMEZONE}"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /data
RUN mkdir /data/scans
WORKDIR /data
