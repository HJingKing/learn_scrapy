# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from ..items import DoubanMovieItem
from scrapy.loader.processors import MapCompose


class DbmovieSpider(CrawlSpider):
    name = 'dbmovie'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//*[contains(@id, "screening")]'),
             callback='parse_item', follow=True),
    )

    # // *[contains( @ id, "screening") and contains( @class , "title")]
    #

    def parse_item(self, response):
        i = ItemLoader(item=DoubanMovieItem(), response=response)
        i.add_xpath("movie", '//*[@property="v:itemreviewed"]/text()')
        i.add_xpath("year", '//*[@class="year"]/text()', re='[0-9]+')
        return i.load_item()
