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

    name = 'fast'
    allowed_domains = ['192.168.56.1']
    start_urls = ['http://192.168.56.1:9312/properties/index_00000.html']

    def parse(self, response):
        # Get the next index URLs and yield Request
        next_selector = response.xpath('//*[contains(@class, "next")]//@href')
        for url in next_selector.extract():
            yield Request(parse.urljoin(response.url, url))

        selectors = response.xpath('//*[@itemtype="http://schema.org/Product"]')
        for selector in selectors:
            yield self.parse_item(selector, response)

        # Get item URLs and yield Request
        # item_selector = response.xpath('//*[contains(@itemprop, "url")]/@href')
        # for url in item_selector.extract():
        #     yield Request(parse.urljoin(response.url, url), callback=self.parse_item)

    def parse_item(self, selector, response):
        """This function parses a property page.
        @url http://192.168.56.1:9312/properties/property_000000.html
        @returns items 1
        @scrapes title price description address image_urls
        @scrapes url project spider server date
        """
        # Create the loader using the response
        it = ItemLoader(item=PropertiesItem(), selector=selector)

        # Load fields using XPath expressions
        it.add_xpath("title", './/*[@itemprop="name"][1]/text()', MapCompose(str.strip, str.title))
        it.add_xpath('price', './/*[@itemprop="price"][1]/text()',
                     MapCompose(lambda i: i.replace(',', ''), float), re='[. 0-9]+')
        it.add_xpath('description', './/*[@itemprop="description"][1]/text()',
                     MapCompose(lambda i: i.replace('\r\n', ' '), str.strip), Join())
        it.add_xpath('address', './/*[@itemtype="http://schema.org/Place"][1]/*/text()')
        it.add_xpath('image_urls', './/*[@itemprop="image"][1]/@src',
                     MapCompose(lambda i: parse.urljoin(response.url, i)))

        # Housekeeping fields
        # it.add_value('url', response.url)
        it.add_xpath('url', './/*[@itemprop="url"][1]/@href', MapCompose(lambda i: parse.urljoin(response.url, i)))
        it.add_value('project', self.settings.get('BOT_NAME'))
        it.add_value('spider', self.name)
        it.add_value('server', socket.gethostname())
        it.add_value('date', datetime.datetime.now())

        # logging.debug("日志")

        return it.load_item()
