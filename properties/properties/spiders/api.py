# -*- coding: utf-8 -*-
# http://192.168.56.1:9312/properties/index_00000.html
import scrapy
import socket
import datetime
import requests
from urllib import parse
from ..items import PropertiesItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
import json
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
import logging


class ApiSpider(scrapy.Spider):

    name = 'api'
    allowed_domains = ['192.168.56.1']
    start_urls = ['http://192.168.56.1:9312/static/']

    def parse(self, response):
        base_url = "http://192.168.56.1:9312/properties/"
        json_url = "http://192.168.56.1:9312/properties/api.json"
        js = requests.get(json_url).json()
        for item in js:
            item_id = item["id"]
            item_title = item["title"]
            url = base_url + "property_%06d.html" % item_id
            yield Request(url, meta={'title': item_title}, callback=self.parse_item)

    def parse_item(self, response):
        """This function parses a property page.
        @url http://192.168.56.1:9312/properties/property_000000.html
        @returns items 1
        @scrapes title price description address image_urls
        @scrapes url project spider server date
        """
        # Create the loader using the response
        i = ItemLoader(item=PropertiesItem(), response=response)

        # Load fields using XPath expressions
        # i.add_xpath("title", '//*[@itemprop="name"][1]/text()', MapCompose(str.strip, str.title))
        i.add_value("title", response.meta['title'], MapCompose(str.strip, str.title))
        i.add_xpath('price', '//*[@itemprop="price"][1]/text()',
                         MapCompose(lambda i: i.replace(',', ''), float), re='[. 0-9]+')
        i.add_xpath('description', '//*[@itemprop="description"][1]/text()',
                         MapCompose(lambda i: i.replace('\r\n', ' '), str.strip), Join())
        i.add_xpath('address', '//*[@itemtype="http://schema.org/Place"][1]/text()')
        i.add_xpath('image_urls', '//*[@itemprop="image"][1]/@src',
                         MapCompose(lambda i: parse.urljoin(response.url, i)))

        # Housekeeping fields
        i.add_value('url', response.url)
        i.add_value('project', self.settings.get('BOT_NAME'))
        i.add_value('spider', self.name)
        i.add_value('server', socket.gethostname())
        i.add_value('date', datetime.datetime.now())

        # logging.debug("日志")

        return i.load_item()
