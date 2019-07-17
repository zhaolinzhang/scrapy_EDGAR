from scrapy.exporters import CsvItemExporter


class TsvCustomExporter(CsvItemExporter):
    def __init__(self, *args, **kwargs):
        kwargs['encoding'] = 'utf-8'
        kwargs['delimiter'] = '\t'
        super(TsvCustomExporter, self).__init__(*args, **kwargs)