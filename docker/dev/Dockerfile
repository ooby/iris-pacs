FROM ubuntu:focal

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install git python3-dev python3-pip gnupg wget apt-utils -y
RUN pip3 install pip --upgrade
RUN pip3 install pydicom pymongo pynetdicom pytest setuptools

ARG TIMEZONE
ENV TZ="${TIMEZONE}"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.4.list
RUN apt-get update
RUN apt-get install mongodb-org -y

ARG MO_CODE
RUN touch /code && echo "${MO_CODE}" > /code
ARG ADDRESS
RUN touch /address && echo "${ADDRESS}" > /address
ARG PORT
RUN touch /port && echo "${PORT}" > /port

RUN mkdir /data
RUN mkdir /data/scans
RUN mkdir /data/db
RUN systemctl start mongod
WORKDIR /data