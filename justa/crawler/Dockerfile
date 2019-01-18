FROM python:3.7.2-slim

WORKDIR /justa

ADD requirements.txt requirements.txt
ADD requirements-dev.txt requirements-dev.txt

RUN apt-get update -y && \
    apt-get install -y build-essential git libffi-dev openssh-client python3-dev && \
    apt-get install -y libxslt-dev libssl-dev && \
    pip install -U pip && \
    pip install -r requirements-dev.txt && \
    apt-get purge -y git build-essential libffi-dev openssh-client python3-dev


ADD scrapy.cfg scrapy.cfg
ADD justa /justa/justa
