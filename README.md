# Justa

## Requirements

* Docker and Docker Compose
* Copy `.env.sample` as `.env` and check if it matches your environment

## Building docker images

Make sure you have pulled and built all needed images by executing:

```console
docker-compose pull
docker-compose build
```

## Running

### Crawler

Having `distrito_federal` as a spider and `DEBUG` as the desired log level:

```console
docker-compose run --rm scrapy scrapy crawl distrito_federal --loglevel=INFO
```

If you need to see the browser running (some crawlers won't work on headless
mode) then export the display and mount the X11 socket:

```console
docker-compose run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
                   scrapy scrapy crawl distrito_federal --loglevel=INFO
```

### Backend

To run the web server, execute:

```console
docker-compose up django
```

Then access it at http://localhost:8000/


#### API endpoints

* List all court orders: `GET /api/court-orders/`
* Details of a court order: `GET /api/court-orders/<id>`
* Create a court order `POST /api/court-orders/`

The `token` value, needed for `POST` requests, should be the hexdigest of the
`SECRET_KET`.

## Testing

```console
docker-compose run --rm <scrapy|django> py.test
```

## Tools

Inside `tools` directory you'll find some scripts to help during project
development:

- `rds2csv.py`: converts RDS files to CSV (only the first data frame), needs to
  install `pandas` and `pyreadr` libraries. Useful to convert some TJ-SP files.
