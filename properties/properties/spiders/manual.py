# -*- coding: utf-8 -*-
# http://192.168.56.1:9312/properties/index_00000.html
import scrapy
import socket
import datetime
from urllib import parse
from ..items import PropertiesItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
import logging


class BasicSpider(scrapy.Spider):

    def __init__(self):
        self.count = 0
        self.max_count = 90

    name = 'manual'
    allowed_domains = ['192.168.56.1']
    start_urls = ['http://192.168.56.1:9312/properties/index_00000.html']

    def parse(self, response):
        # Get the next index URLs and yield Request
        next_selector = response.xpath('//*[contains(@class, "next")]//@href')
        for url in next_selector.extract():
            yield Request(parse.urljoin(response.url, url))
        # Get item URLs and yield Request
        item_selector = response.xpath('//*[contains(@itemprop, "url")]/@href')
        for url in item_selector.extract():
            self.count += 1
            if self.count > self.max_count:
                raise CloseSpider()
            else:
                yield Request(parse.urljoin(response.url, url), callback=self.parse_item)

    def parse_item(self, response):
        """This function parses a property page.
        @url http://192.168.56.1:9312/properties/property_000000.html
        @returns items 1
        @scrapes title price description address image_urls
        @scrapes url project spider server date
        """
        # Create the loader using the response
        itemls = ItemLoader(item=PropertiesItem(), response=response)

        # Load fields using XPath expressions
        itemls.add_xpath("title", '//*[@itemprop="name"][1]/text()', MapCompose(str.strip, str.title))
        itemls.add_xpath('price', '//*[@itemprop="price"][1]/text()',
                         MapCompose(lambda i: i.replace(',', ''), float), re='[. 0-9]+')
        itemls.add_xpath('description', '//*[@itemprop="description"][1]/text()',
                         MapCompose(lambda i: i.replace('\r\n', ' '), str.strip), Join())
        itemls.add_xpath('address', '//*[@itemtype="http://schema.org/Place"][1]/text()')
        itemls.add_xpath('image_urls', '//*[@itemprop="image"][1]/@src',
                         MapCompose(lambda i: parse.urljoin(response.url, i)))

        # Housekeeping fields
        itemls.add_value('url', response.url)
        itemls.add_value('project', self.settings.get('BOT_NAME'))
        itemls.add_value('spider', self.name)
        itemls.add_value('server', socket.gethostname())
        itemls.add_value('date', datetime.datetime.now())

        # logging.debug("日志")

        return itemls.load_item()
