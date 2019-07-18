import scrapy

from scrapy_EDGAR.spiders import BaseSpider


class EDGARSpiderCompName(BaseSpider):
    name = "EDGARSpiderCompName"
    allowed_domains = ["sec.gov"]

    def __init__(self, company_name=None, *args, **kwargs):
        super(EDGARSpiderCompName, self).__init__(*args, **kwargs)
        self.company_name = company_name
        self.CIK = None

        if self.company_name is None:
            raise ValueError("Error: Argument 'company_name' could NOT be None")

    def start_requests(self):
        # replace 1 or more whitespace chars except the newline and a tab by '+'
        company_name_trim = self.company_name.strip().replace(r"[^\S\n\t]+", '+')
        yield scrapy.Request(self.company_name_lookup_url % company_name_trim)

    # main method, using company_name, find CIK
    def parse(self, response):
        sel = scrapy.Selector(response)
        # Get different page format here
        # if searching company_name only return 1 result, extract that CIK
        if sel.xpath('//span[@class="companyName"]'):
            self.company_name = sel.xpath('//span[@class="companyName"]/text()').extract_first()
            cik_temp = sel.xpath('//span[@class="companyName"]/a/text()').extract_first()
            self.CIK = cik_temp.split(" ")[0]
            yield scrapy.Request(self.CIK_lookup_url % self.CIK, callback=self.CIK_parse)
        # if searching company_name return multiple result, extract the first result's CIK
        else:
            sites = sel.xpath('//div/table/tr')
            for site in sites:
                if site.xpath('td/a/@href'):
                    self.CIK = site.xpath('td[1]/a/text()').extract_first()
                    yield scrapy.Request(self.CIK_lookup_url % self.CIK, callback=self.CIK_parse)

                if self.CIK is not None:
                    break
