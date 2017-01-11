# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class tmpItem(scrapy.Item):
    batch = scrapy.Field()
    json = scrapy.Field()
    # date = scrapy.Field()
    # path = scrapy.Field()
