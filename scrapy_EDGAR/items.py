# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ReportItem(scrapy.Item):
    name_of_issuer = scrapy.Field()
    title_of_class = scrapy.Field()
    cusip = scrapy.Field()
    value = scrapy.Field()
    ssh_prnamt = scrapy.Field()
    ssh_prnamt_type = scrapy.Field()
    investment_discretion = scrapy.Field()
    voting_authority_sole = scrapy.Field()
    voting_authority_shared = scrapy.Field()
    voting_authority_none = scrapy.Field()
    filling_date = scrapy.Field()
