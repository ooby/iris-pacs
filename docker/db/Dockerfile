FROM mongo:4.4.1-bionic

ARG TIMEZONE
ENV TZ="${TIMEZONE}"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG MO_CODE
RUN touch /code && echo "${MO_CODE}" > /code

WORKDIR /data