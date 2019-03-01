FROM python:3.7.2-slim

WORKDIR /justa

# Install pipenv (needed by both images, so we can benefit of docker commit
# cache here)
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -U pipenv

# Install Python dependencies
ADD Pipfile Pipfile
ADD Pipfile.lock Pipfile.lock
ADD pytest.ini pytest.ini
RUN pipenv install --dev --system
