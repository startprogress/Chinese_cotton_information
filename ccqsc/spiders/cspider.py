#!/usr/bin/python
#-*- coding: utf-8 -*-
import os
import scrapy
import datetime
import json
from scrapy.http.request import Request

# ccqsc网站拿到json数据
from ccqsc.items import ccqscItem
class ccqsc(scrapy.Spider):
    name = "ccqsc"
    # 路径默认为"data/"
    year = datetime.datetime.now().strftime("%Y")
    def __init__(self, cookie, path='data/', year=year):
        self.cookie = cookie
        self.path = path
        self.year = year

    allowed_domains = ["ccqsc.gov.cn", "cottoneasy.com", "cottonchina.org"]
    start_urls = [
        "http://www.cottoneasy.com/storage/maStorageProgressListInit"
    ]
    #第一层，拿到42个储运站的URL
    def parse(self, response):
        # 将时间范围拆分放入list中
        date_range = []
        curr_date = datetime.date(int(self.year), 1, 1)
        end_date = datetime.date(int(self.year), 12, 31)
        while curr_date != end_date:
            date_range.append(str(curr_date))
            curr_date += datetime.timedelta(days=1)
        for date_i in date_range:
            for i in range(0, len(response.xpath('//a[@class="fsize_12 btn-link pr_5"]')), 7):
                originreq = "".join(response.xpath(
                    '//a[@class="fsize_12 btn-link pr_5"]')[i].xpath('@href').extract())
                req = "http://www.cottoneasy.com/" + originreq[:-10] + date_i
                yield Request(req, callback=self.parse2)

    #第二层，拿到每一批次的编号
    def parse2(self, response):
        item = ccqscItem()
        #只要批次号，所以每8个td才取一次
        for i in range(8, len(response.xpath('//td')), 8):
            batchnum = "".join(response.xpath(
                '//td')[i].xpath('text()').extract())
            req = "http://www.ccqsc.gov.cn/query/compareBatchInfoData.action?batchCodeInput=" + batchnum
            item['batch'] = batchnum
            yield Request(req, meta={'item': item, 'batchnum': batchnum}, cookies={'JSESSIONID':self.cookie}, callback=self.parse3)

    #第三层，依据编号到ccsqc网站拿json数据存入
    def parse3(self, response):
        item = response.meta['item']
        batchnum = response.meta['batchnum']
        item['json'] = json.loads(response.body_as_unicode())
        if os.path.exists(self.path + self.year):
            pass
        else:
            os.makedirs(self.path + self.year)
        with open(self.path + self.year + '/' + batchnum + '.json', 'wb') as f:
            f.write(json.dumps(dict(item['json'])))
        yield item



# 大渊博网站
from ccqsc.items import dyb_Item
# obtain the urls of entrepot
class dybcotton(scrapy.Spider):
    name = "dybcotton"
    def __init__(self, year):
        self.year = year
    allowed_domains = ["dybcotton.com"]
    start_urls = [
        "http://www.dybcotton.com/entrepot"
    ]

    def parse(self, response):
        for sel in response.xpath('//div[@class="col-sm-6 col-md-4 col-lg-3 "]'):
            yield Request("http://www.dybcotton.com" + "".join(sel.xpath('div/a/@href').extract()).strip() + "?productionYear=" + self.year, callback=self.parse2)



    def parse2(self, response):
        #item = dyb_Item()
        a_num = len(response.xpath('//html/body/div[4]/div[2]/div[2]/div[2]/div/a'))
        page_info = ''.join(response.xpath('//html/body/div[4]/div[2]/div[2]/div[2]/div/a[' + str(a_num) + ']/@href').extract()).strip()
        page_max = page_info[(page_info.rfind("=") + 1):]
        page_to = page_info[:(page_info.rfind("=") + 1)]
        for i in range(1, int(page_max)):
            #item['title'] = "".join(sel.xpath('div/a/div[1]/h4/text()').extract()).strip()
            #item['link'] = "http://www.dybcotton.com" + page_to + str(i)
            yield Request("http://www.dybcotton.com" + page_to + str(i), callback=self.parse3)

    def parse3(self, response):
        item = dyb_Item()
        for i in range(1, len(response.xpath('//html/body/div[4]/div[2]/div[2]/table[2]/tr')),2):
            finalurl = "http://www.dybcotton.com" + "".join(response.xpath('/html/body/div[4]/div[2]/div[2]/table[2]/tr[' + str(i) + ']/td[1]/a/@href').extract())
	    item['link'] = finalurl
            yield Request(finalurl, callback=self.parse4)

    #def parse4(self, response):
	# 根据自己所需信息制定进行页面解析	
