import scrapy

from scrapy_EDGAR.items import ReportItem


class EDGARSpiderCompName(scrapy.Spider):
    name = "EDGARSpiderCompName"
    allowed_domains = ["sec.gov"]
    base_url = 'https://www.sec.gov'
    CIK_lookup_url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK=%s&owner=exclude&action=getcompany"
    company_name_lookup_url = "https://www.sec.gov/cgi-bin/browse-edgar?company=%s&match=contains&filenum=&State=&" + \
                              "Country=&SIC=&myowner=exclude&action=getcompany"
    filling_date = None

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

    # Do similar job in EDGARSpiderCIK, since CIK is known
    # main method, find the most recent '13F-HR' report
    # Example webpage:
    # https://www.sec.gov/cgi-bin/browse-edgar?CIK=0001166559&owner=exclude&action=getcompany&Find=Search
    def CIK_parse(self, response):
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

    # 2nd depth method, find the information table
    # Example webpage:
    # https://www.sec.gov/Archives/edgar/data/1166559/000110465919029714/0001104659-19-029714-index.htm
    def CIK_detail_file_page_parse(self, response):
        sel = scrapy.Selector(response)
        sites = sel.xpath('//table/tr')
        xml_file_link = ""
        html_file_link = ""
        for site in sites:
            if site.xpath('td/a/@href'):
                doc_type = site.xpath('td[4]/text()').extract_first()
                file_type = site.xpath('td/a/text()').extract_first()
                file_link = self.base_url + site.xpath('td/a/@href').extract_first()

                if doc_type == 'INFORMATION TABLE' and file_type.endswith(".xml"):
                    xml_file_link = file_link
                elif doc_type == 'INFORMATION TABLE' and file_type.endswith(".html"):
                    html_file_link = file_link

        if xml_file_link != "":
            yield scrapy.Request(xml_file_link, callback=self.xml_file_flattener)
        elif html_file_link != "":
            yield scrapy.Request(html_file_link, callback=self.html_file_flattener)

    # 3rd depth method, extract the information in XML
    def xml_file_flattener(self, response):
        # Need to register namespace here, otherwise it does NOT return anything
        sel = scrapy.Selector(response, type='xml')
        sel.register_namespace("s", "http://www.sec.gov/edgar/document/thirteenf/informationtable")
        sites = sel.xpath("//s:infoTable")
        items = []
        for site in sites:
            item = ReportItem()
            item['name_of_issuer'] = site.xpath('./s:nameOfIssuer/text()').extract_first()
            item['title_of_class'] = site.xpath('./s:titleOfClass/text()').extract_first()
            item['cusip'] = site.xpath('./s:cusip/text()').extract_first()
            item['value'] = site.xpath('./s:value/text()').extract_first()
            item['ssh_prnamt'] = site.xpath('./s:shrsOrPrnAmt').xpath('./s:sshPrnamt/text()').extract_first()
            item['ssh_prnamt_type'] = site.xpath('./s:shrsOrPrnAmt').xpath('./s:sshPrnamtType/text()').extract_first()
            item['investment_discretion'] = site.xpath('./s:investmentDiscretion/text()').extract_first()
            item['voting_authority_sole'] = site.xpath('./s:votingAuthority').xpath('./s:Sole/text()').extract_first()
            item['voting_authority_shared'] = site.xpath('./s:votingAuthority').xpath(
                './s:Shared/text()').extract_first()
            item['voting_authority_none'] = site.xpath('./s:votingAuthority').xpath('./s:None/text()').extract_first()
            item['filling_date'] = self.filling_date
            items.append(item)
        return items

    # 3rd depth method, extract the information in HTML
    def html_file_flattener(self, response):
        pass
