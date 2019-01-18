FROM python:3.7.2-slim

WORKDIR /justa

ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock

RUN pip install -U pip && \
    pip install -U pipenv && \
    pipenv install --dev --system

ADD pytest.ini pytest.ini
