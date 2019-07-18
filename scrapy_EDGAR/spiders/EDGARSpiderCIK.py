import scrapy

from scrapy_EDGAR.spiders import BaseSpider


class EDGARSpiderCIK(BaseSpider):
    name = "EDGARSpiderCIK"
    allowed_domains = ["sec.gov"]

    def __init__(self, CIK=None, *args, **kwargs):
        super(EDGARSpiderCIK, self).__init__(*args, **kwargs)
        self.CIK = CIK

        if self.CIK is None:
            raise ValueError("Error: Argument 'CIK' could NOT be None")

    def start_requests(self):
        yield scrapy.Request(self.CIK_lookup_url % self.CIK)

    # main method, find the most recent '13F-HR' report
    # Example webpage:
    # https://www.sec.gov/cgi-bin/browse-edgar?CIK=0001166559&owner=exclude&action=getcompany&Find=Search
    def parse(self, response):
        sel = scrapy.Selector(response)
        sites = sel.xpath('//div/table/tr')
        for site in sites:
            if site.xpath('td/a/@href'):
                filling_type = site.xpath('td[1]/text()').extract_first()
                filling_link = self.base_url + site.xpath('td/a[@id="documentsbutton"]/@href').extract_first()
                self.filling_date = site.xpath('td[4]/text()').extract_first()

                # if the current file starts with '13F-HR'
                # then got the most recent report, break the loop
                if filling_type.startswith("13F-HR"):
                    yield scrapy.Request(filling_link, callback=self.CIK_detail_file_page_parse)
                    break
