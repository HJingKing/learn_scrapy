# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import socket
import datetime
from urllib import parse
from ..items import PropertiesItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join


class EasySpider(CrawlSpider):
    name = 'easy'
    allowed_domains = ['192.168.56.1']
    start_urls = ['http://192.168.56.1:9312/properties/index_00000.html']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//*[contains(@class, "next")]'), follow=True),
        Rule(LinkExtractor(restrict_xpaths='//*[contains(@itemprop, "url")]'), callback='parse_item', follow=True)
    )

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
        i.add_xpath("title", '//*[@itemprop="name"][1]/text()', MapCompose(str.strip, str.title))
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
