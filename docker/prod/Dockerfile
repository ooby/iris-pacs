FROM ubuntu:focal

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install git python3-dev python3-pip gnupg wget apt-utils -y
RUN pip3 install pip --upgrade
RUN pip3 install pika pydicom pymongo pynetdicom pytest setuptools

ARG TIMEZONE
ENV TZ="${TIMEZONE}"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG MO_CODE
RUN touch /code && echo "${MO_CODE}" > /code
ARG ADDRESS
RUN touch /address && echo "${ADDRESS}" > /address
ARG PORT
RUN touch /port && echo "${PORT}" > /port
ARG MQ_HOST 
RUN touch /mq_host && echo "${MQ_HOST}" > /mq_host
ARG DB_ADDRESS
RUN touch /db_address && echo "${DB_ADDRESS}" > /db_address
ARG DB_PORT
RUN touch db_port && echo "${DB_PORT}" > /db_port


WORKDIR /
RUN git clone https://github.com/ooby/iris-pacs iris-pacs

RUN mkdir /data
RUN mkdir /data/scans
WORKDIR /iris-pacs

CMD pip3 install -e . && python3 start.py $(cat /address) $(cat /port) $(cat /mq_host) $(cat /db_address) $(cat /db_port)
