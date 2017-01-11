#!/usr/bin/python
#-*- coding: utf-8 -*-
import os
import scrapy
import datetime
import json
# from scrapy import log
from ccqsc.items import tmpItem
from scrapy.http.request import Request
# scrapy.log.start(logfile='error.log', loglevel=ERROR, logstdout=None)

class ccqsc(scrapy.Spider):
    name = "ccqsc"
    #如果不提供参数，日期默认为系统当前日期，路径默认为"data/"
    today =  datetime.datetime.now().strftime("%Y-%m-%d")
    def __init__(self, date=today, path='data/'):
        if path[-1] != '/':
            path = path + '/'
        self.date = date
        self.path = path

    allowed_domains = ["ccqsc.gov.cn", "cottoneasy.com", "cottonchina.org"]
    start_urls = [
        "http://www.cottoneasy.com/storage/maStorageProgressListInit"
    ]
    #第一层，拿到42个储运站的URL
    def parse(self, response):
        # 将时间范围拆分放入list中
        if len(self.date) > 10:
            date_range = []
            date1 = self.date[0:10]
            date2 = self.date[11:]
            curr_date = datetime.date(
                int(date1[0:4]), int(date1[5:7]), int(date1[8:10]))
            end_date = datetime.date(
                int(date2[0:4]), int(date2[5:7]), int(date2[8:10]))
            while curr_date != end_date:
                date_range.append(str(curr_date))
                curr_date += datetime.timedelta(days=1)
        else:
            date_range = [self.date]
        for date_i in date_range:
            for i in range(0, len(response.xpath('//a[@class="fsize_12 btn-link pr_5"]')), 7):
                originreq = "".join(response.xpath(
                    '//a[@class="fsize_12 btn-link pr_5"]')[i].xpath('@href').extract())
                req = "http://www.cottoneasy.com/" + originreq[:-10] + date_i
                yield Request(req, callback=self.parse2)
    #第二层，拿到每一批次的编号
    def parse2(self, response):
        item = tmpItem()
        #只要批次号，所以每8个td才取一次
        for i in range(8, len(response.xpath('//td')), 8):
            batchnum = "".join(response.xpath(
                '//td')[i].xpath('text()').extract())
            req = "http://www.ccqsc.gov.cn/query/compareBatchInfoData.action?batchCodeInput=" + batchnum
            item['batch'] = batchnum
            yield Request(req, meta={'item': item, 'batchnum': batchnum}, callback=self.parse3)
    #第三层，依据编号到ccsqc网站拿json数据存入
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
