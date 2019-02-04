# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class CourtOrder(Item):
    """Court orders with full text"""
    number = Field()
    name = Field()
    date = Field()
    text = Field()
    body = Field()


class CourtOrderReference(Item):
    """Number of court orders to be processed later on"""
    number = Field()
    source = Field()
