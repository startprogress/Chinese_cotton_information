import os
import scrapy
import json
# from scrapy import log
from ccqsc.items import tmpItem
from scrapy.http.request import Request
# scrapy.log.start(logfile='error.log', loglevel=ERROR, logstdout=None)


class ccqsc(scrapy.Spider):
    name = "ccqsc"

    def __init__(self, date=None, path='data/'):
        self.date = date
        self.path = path

    allowed_domains = ["ccqsc.gov.cn", "cottoneasy.com", "cottonchina.org"]
    start_urls = [
        "http://www.cottoneasy.com/storage/maStorageProgressListInit"
    ]

    def parse(self, response):
        #item = tmpItem()
        for i in range(0, len(response.xpath('//a[@class="fsize_12 btn-link pr_5"]')), 7):
            originreq = "".join(response.xpath(
                '//a[@class="fsize_12 btn-link pr_5"]')[i].xpath('@href').extract())
            req = "http://www.cottoneasy.com/" + originreq[:-10] + self.date
            yield Request(req, callback=self.parse2)

    def parse2(self, response):
        item = tmpItem()
        for i in range(8, len(response.xpath('//td')), 8):
            batchnum = "".join(response.xpath(
                '//td')[i].xpath('text()').extract())
            req = "http://www.ccqsc.gov.cn/query/compareBatchInfoData.action?batchCodeInput=" + batchnum
            item['batch'] = batchnum
            yield Request(req, meta={'item': item, 'batchnum': batchnum}, callback=self.parse3)

    def parse3(self, response):
        item = response.meta['item']
        batchnum = response.meta['batchnum']
        #item['date'] = self.date
        #item['path'] = self.path
        item['json'] = json.loads(response.body_as_unicode())
        if os.path.exists(self.path + self.date):
            pass
        else:
            os.makedirs(self.path + self.date)
        with open(self.path + self.date + '/' + batchnum + '.json', 'wb') as f:
            f.write(json.dumps(dict(item['json'])))
        yield item
