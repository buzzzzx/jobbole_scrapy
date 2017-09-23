# -*- coding: utf-8 -*-
import scrapy
import re
import time
import json
import requests
import os.path

try:
    from PIL import Image
except:
    pass


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Host": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
    }

    def parse(self, response):
        pass

    # spider入口方法
    def start_requests(self):
        # 重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
    #     return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login)]  # 返回值必须是一个序列
    #
    # def login(self, response):
    #     response_text = response.text
    #     match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
    #     _xsrf = ''
    #     if match_obj:
    #         _xsrf = (match_obj.group(1))
        _xsrf = self.get_xsrf()

        if _xsrf:
            self.headers['X-Xsrftoken'] = _xsrf
            captcha = self.get_captcha()
            post_url = 'https://www.zhihu.com/login/phone_num'
            postdata = {
                '_xsrf': _xsrf,
                'password': "batman123",
                'phone_num': "17780625910",
                'captcha': captcha,
            }

            return [scrapy.FormRequest(
                url=post_url,
                formdata=postdata,
                headers=self.headers,
                callback=self.check_login
            )]

    def get_xsrf(self):
        # 获取表单数据中的_xsrf
        index_url = 'https://www.zhihu.com/#signin'
        response = requests.get(index_url, headers=self.headers)
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
        if match_obj:
            return match_obj.group(1)
        else:
            return ""

    # 获取验证码
    def get_captcha(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        r = requests.get(captcha_url, headers=self.headers)
        with open('captcha.jpg', 'wb') as f:
            f.write(r.content)
            f.close()
        # 用pillow 的 Image 显示验证码
        # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
        captcha = input("please input the captcha\n>")
        return captcha

    # 验证是否登陆成功
    def check_login(self, response):
        text_json = json.load(response.text)
        if 'msg' in text_json and text_json['msg'] == "登陆成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)

                # 原本scrapy中的scrapy.Request会保存访问过程中的cookie信息其实这里面也是用的cookiejar

