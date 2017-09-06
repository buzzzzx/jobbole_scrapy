# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobboleArticleItem
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader
from ArticleSpider.items import ArticalItemLoader


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
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            post_url = post_node.css("::attr(href)").extract_first("")
            image_url = post_node.css("img::attr(src)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_detail)

        # 获取下一页的url并交给scrapy进行下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 提取文章的具体字段

        article_item = JobboleArticleItem()

        # xpath选择器
        #
        # front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        # title = response.xpath("//div[@class='entry-header']/h1/text()").extract()[0]
        # create_time = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace("·","").strip()
        # praise_num = response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0]
        # fav_num = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        # match_re = re.match(".*?(\d+).*", fav_num)
        # if match_re:
        #     fav_num = int(match_re.group(1))
        # else:
        #     fav_num = 0
        #
        # comment_num = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]
        # match_re = re.match(".*?(\d+).*", comment_num)
        # if match_re:
        #     comment_num = int(match_re.group(1))
        # else:
        #     comment_num = 0
        #
        # content = response.xpath("//div[@class='entry']").extract()[0]
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["title"] = title
        # try:
        #     create_time = datetime.datetime.strptime(create_time, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_time = datetime.datetime.now().date()
        # article_item["create_time"] = create_time
        # article_item["url"] = response.url
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_num"] = praise_num
        # article_item["comment_num"] = comment_num
        # article_item["fav_num"] = fav_num
        # article_item["content"] = content
        # article_item["tags"] = tags

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
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)

        # 通过ItemLoader加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticalItemLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_time", ".entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_num", "span[class*='vote-post-up'] h10::text")
        item_loader.add_css("comment_num", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_num", "span[class*='bookmark-btn']::text")
        item_loader.add_css("content", "div.entry")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")

        article_item = item_loader.load_item()

        yield article_item  # 使用yield可以将article_item自动传递到pipelines里面去



