# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):

        """
        1. 获取文章列表的文章url并交给scrapy下载后用解析函数解析
        2. 获取下一页的url并交给scrapy进行下载
        """

        # 获取文章列表的文章url并交给scrapy下载后用解析函数解析
        post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
        for post_url in post_url:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_detail)

        # 获取下一页的url并交给scrapy进行下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 提取文章的具体字段
        # xpath
        title = response.xpath("//div[@class='entry-header']/h1/text()").extract()[0]
        create_time = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace("·","").strip()
        praise_num = response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0]
        fav_num = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        match_re = re.match(".*?(\d+).*", fav_num)
        if match_re:
            fav_num = int(match_re.group(1))
        else:
            fav_num = 0

        comment_num = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]
        match_re = re.match(".*?(\d+).*", comment_num)
        if match_re:
            comment_num = int(match_re.group(1))
        else:
            comment_num = 0

        content = response.xpath("//div[@class='entry']").extract()[0]
        tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        tag_list = [element for element in tag_list if not element.strip().endwith("评论")]
        tags = ",".join(tag_list)


        # # css选择器
        #
        # title = response.css(".entry-header h1::text").extract()[0]
        # create_time = response.css(".entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·","").strip()
        # praise_num = response.css("span[class*='vote-post-up'] h10::text").extract()[0]
        # fav_num = response.css("span[class*='bookmark-btn']::text").extract()[0]
        # match_re = re.match(".*?(\d+).*", fav_num)
        # if match_re:
        #     fav_num = match_re.group(1)
        #
        # commen_num = response.css("a[href='#article-comment'] span::text").extract()[0]
        # match_re = re.match(".*?(\d+).*", comment_num)
        # if match_re:
        #     comment_num = match_re.group(1)
        #
        # content = response.css("div.entry").extract()[0]
        # tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # tag_list = [element for element in tag_list if not element.strip().endwith("评论")]
        # tags = ",".join(tag_list)




