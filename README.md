# Open-Jus

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

If you need to see the browser running you must replace the Firefox or Chrome
images with `selenium/standalone-firefox-debug` and/or
`selenium/standalone-chrome-debug` and then connect to its VNC server (Chrome
will be exported to port 5900 and Firefox to 5901).

Example for Firefox:

```console
docker-compose stop firefox
docker-compose rm -f firefox
sed -i 's/standalone-firefox$/standalone-firefox-debug/' docker-compose.yml
docker-compose up -d firefox

# Now, run the scraper and in parallel connect to VNC:
docker-compose run --rm scrapy scrapy crawl budget_ce -a headless=false --loglevel=INFO
xtightvncviewer 127.0.0.1:5901  # The password is "secret"
```

### Backend

To run the web server, execute:

```console
docker-compose up django
```

Then access it at http://localhost:8000/


#### API endpoints

##### General court orders

* List all court orders:<br>`GET /api/court-orders/`
* Details of a court order:<br>`GET /api/court-orders/<id>`
* Create a court order:<br>`POST /api/court-orders/`

The `token` value, needed for `POST` requests, should be the hexdigest of the
`SECRET_KET`.

##### eSAJ court orders

* List all court orders:<br>`GET /api/court-orders-esaj/`
* Details of a court order:<br>`GET /api/court-orders-esaj/<id>`


## Testing

```console
docker-compose run --rm <scrapy|django> py.test
```

## Tools

Inside `tools` directory you'll find some scripts to help during project
development:

- `rds2csv.py`: converts RDS files to CSV (only the first data frame), needs to
  install `pandas` and `pyreadr` libraries. Useful to convert some TJ-SP files.
