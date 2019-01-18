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

#### API endpoints

* List all court orders:<br>`GET /api/court-orders/`
* Details of a court order:<br>`GET /api/court-orders/<id>`
* Create a court order:<br>`POST /api/court-orders/`

The `token` value, needed for `POST` requests, should be the hexdigest of the `SECRET_KET`.

## Testing

```console
$ docker-compose run --rm <service> py.test
```

In which `<service>` can be either `scrapy` or `django`.
