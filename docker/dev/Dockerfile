FROM ubuntu:focal

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install git python3-dev python3-pip -y
RUN pip3 install pip --upgrade
RUN pip3 install pydicom pymongo pynetdicom pytest setuptools

ARG TIMEZONE
ENV TZ="${TIMEZONE}"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG MO_CODE
RUN touch /code && echo "${MO_CODE}" > /code
ARG ADDRESS
RUN touch /address && echo "${ADDRESS}" > /address
ARG PORT
RUN touch /port && echo "${PORT}" > /port

RUN mkdir /data
RUN mkdir /data/scans
RUN mkdir /data/db
WORKDIR /data