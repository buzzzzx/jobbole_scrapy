# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

import codecs
import json
import MySQLdb
import MySQLdb.cursors


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


# 自定义json文件导出
class JsonWithEncodingPipline(object):
    def __init__(self):
        self.file = codecs.open("article.json", 'w', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


# 用scrapy自带的json exporter导出json文件
class JsonExporterPiplines(object):
    def __init__(self):
        self.file = open('articlejsonexporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def closed_spide(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# 采用同步的机制写入mysql
class MysqlPipline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'batman123', 'bolearticle_spider', charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article(title, url, url_object_id, create_time, fav_num) VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql,
                            (item['title'], item['url'], item['url_object_id'], item['create_time'], item['fav_num']))
        self.conn.commit()


# 采用twisted框架提供的数据库插入异步化的操作(连接词)
class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):  # 方法名称固定，自动被scrapy调用
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
                    insert into article(title, url, url_object_id, create_time, fav_num) VALUES (%s, %s, %s, %s, %s)
                """
        cursor.execute(insert_sql,
                       (item['title'], item['url'], item['url_object_id'], item['create_time'], item['fav_num']))


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, values in results:
            image_file_path = values['path']

        item['front_image_path'] = image_file_path

        return item
