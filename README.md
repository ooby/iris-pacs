## Simple IRIS PACS

## Предварительная настройка ОС и машины

1. Ubuntu 20.04 x64
2. docker ver. >= 19.03

## Шаги по запуску

1. Завести медицинскую организацию на `https://irisweb.ru` и получить идентификатор `MO_CODE`
2. Скачать Dockerfile и собрать docker-образ
```bash
git clone https://github.com/ooby/iris-pacs
cd iris-pacs
docker build docker -t iris-pacs --build-arg TIMEZONE="Asia/Yakutsk" --build-arg MO_CODE="5f1a32c2490e6a7389fc121c" --build-arg ADDRESS="0.0.0.0" --build-arg PORT="104"
# TIMEZONE - часовой пояс, где находится МО, MO_CODE - идентификатор, полученный на 1 шаге, ADDRESS - IP-адрес, PORT - порт
```
3. Запустить `docker`-контейнер c правильными аргументами
```bash
cd /media/user/storage
docker run --restart always -dit -v $PWD:/data -p 104:104 iris-pacs
```

### Все вопросы на info@sciberia.io