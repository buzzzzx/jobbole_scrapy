# -*- coding: utf-8 -*-
import scrapy


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/112281/']

    def parse(self, response):
        re_selector = response.xpath('//*[@id="post-112281"]/div[1]/h1/text()')
        pass