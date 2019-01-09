import scrapy


class DistritoFederalSpider(scrapy.Spider):
    name = 'distrito_federal'
    allowed_domains = ['tjdft.jus.br']

    def parse(self, response):
        pass
