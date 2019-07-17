# -*- coding: utf-8 -*-

from scrapy import signals

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy_EDGAR.exporters import TsvCustomExporter


class CustomPipeline(object):

    items_field = ['name_of_issuer', 'title_of_class', 'cusip', 'value', 'ssh_prnamt',
                   'ssh_prnamt_type', 'investment_discretion', 'voting_authority_sole', 'voting_authority_shared',
                   'voting_authority_none', 'filling_date']

    def __init__(self):
        self.files = {}
        self.exporter = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file_name = None
        if spider.CIK:
            file_name = '%s_report.tsv' % spider.CIK
        elif spider.company_name:
            file_name = '%s_report.tsv' % spider.company_name
        file = open(file_name, 'w+b')
        self.files[spider] = file
        self.exporter = TsvCustomExporter(file)
        self.exporter.fields_to_export = self.items_field
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
