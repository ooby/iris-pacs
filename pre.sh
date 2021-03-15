#!/bin/sh
docker pull mongo
docker pull rabbitmq:3.8.9
docker run --restart always -dit -p 27017:27017 --name iris-db mongo
docker run --restart always -dit -p 5672:5672 --name iris-mq rabbitmq:3.8.9
