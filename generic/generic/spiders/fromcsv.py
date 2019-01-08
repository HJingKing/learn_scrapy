# -*- coding: utf-8 -*-
import scrapy
import csv
from scrapy.http import Request
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader


class FromcsvSpider(scrapy.Spider):
    name = 'fromcsv'

    def start_requests(self):
        with open("todo.csv", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for line in reader:
                request = Request(line.pop('url'))
                request.meta['fields'] = line
                yield request

    def parse(self, response):
        item = Item()
        l = ItemLoader(item=item, response=response)
        for name, xpath in response.meta['fields'].items():
            if xpath:
                item.fields[name] = Field()
                l.add_xpath(name, xpath)
        return l.load_item()
