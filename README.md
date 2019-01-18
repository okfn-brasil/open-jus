# Justa

## Requirements

* Docker and Docker Compose
* Copy `.env.sample` as `.env` and check if it matches your environment

## Running

### Crawler

Having `distrito_federal` as a spider and `INFO` as the desired log level:

```console
$ docker-compose run --rm scrapy scrapy crawl distrito_federal --loglevel=DEBUG
```

### Web server

```console
$ docker-compose up django
```

## Testing

```console
$ docker-compose run --rm <service> py.test
```

In which `<service>` can be either `scrapy` or `django`.
