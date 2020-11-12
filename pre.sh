#!/bin/sh
docker pull mongo
docker pull rabbitmq
docker run --restart always -dit -p 27017:27017 --name iris-db mongo
docker run --restart always -dit -p 4369:4369 -p 5671:5671 -p 5672:5672 -p 15691:15691 -p 15692:15692 -p 25672:25672 --name iris-mq rabbitmq
