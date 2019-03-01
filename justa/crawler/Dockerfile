FROM python:3.7.2-slim

WORKDIR /justa

# Install pipenv (needed by both images, so we can benefit of docker commit
# cache here)
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -U pipenv

# Install needed system dependencies and cleanup
RUN apt-get update -y && \
    apt-get install -y build-essential git libffi-dev openssh-client \
                       python3-dev libxslt-dev libssl-dev && \
    apt-get clean

# Install Python dependencies
ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock
RUN pipenv install --dev --system

# Add scraper code
ADD scrapy.cfg scrapy.cfg
ADD justa /justa/justa
