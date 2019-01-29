# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class CourtOrder(Item):
    number = Field()
    name = Field()
    date = Field()
    text = Field()
    body = Field()
