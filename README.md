# Justa

## Requirements & dependencies

* Docker and Docker Compose

## Running

Having `distrito_federal` as a spider and `INFO` as the desired log level:

```console
$ docker-compose run --rm scrapy scrapy crawl distrito_federal --loglevel=DEBUG
```

## Testing

```console
$ docker-compose run --rm scrapy py.test
```
