FROM python:3.7.2-alpine

WORKDIR /justa

ADD requirements.txt requirements.txt
ADD requirements-dev.txt requirements-dev.txt

RUN apk update && \
    apk add --virtual .build-dependencies \
        build-base \
        git \
        libffi-dev \
        openssh \
        python3-dev && \
    apk add libxslt-dev openssl-dev && \
    pip install -U pip && \
    pip install -r requirements-dev.txt && \
    apk del .build-dependencies

ADD scrapy.cfg scrapy.cfg
ADD justa /justa/justa
