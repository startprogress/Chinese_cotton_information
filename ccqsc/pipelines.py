# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# class CcqscPipeline(object):
#    def process_item(self, item, spider):
#        return item
import codecs
import json
from scrapy import signals


class JsonWithEncodingPipeline(object):

    def process_item(self, item, spider):
        self.file = codecs.open(
            item['path'] + item['date'] + '/' + item['batch'] + '.json', 'wb', encoding='utf-8')
        line = json.dumps(item['json'], ensure_ascii=False,
                          sort_keys=False) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()
