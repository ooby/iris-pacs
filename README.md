## Simple IRIS PACS

## Предварительная настройка ОС и машины

1. Ubuntu 20.04 x64
2. docker ver. >= 19.03
3. pynetdicom

## Шаги по запуску

0. Запустить `pre.sh` для скачивания и запуска контейнеров очереди и СУБД
1. Сгенерировать файл конфигурации `config.ini` с помощью `configurator.py` из папки `utils`
2. Скачать Dockerfile и собрать docker-образ
```bash
git clone https://github.com/ooby/iris-pacs
cd iris-pacs
docker build docker/prod -t iris-pacs --build-arg TIMEZONE="Asia/Yakutsk"
```
3. Запустить `docker`-контейнер c правильными аргументами
```bash
docker run --log-opt max-size=512k --log-opt max-file=1 --restart always -dit -v $PWD:/data -p 104:104 iris-pacs
```

### Все вопросы на info@sciberia.io
