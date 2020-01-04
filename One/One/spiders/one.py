# -*- coding: utf-8 -*-
import re
import scrapy
from urllib import parse
from ..items import OneItem


class OneSpider(scrapy.Spider):
    name = 'one'
    allowed_domains = ['www.manhuaniu.com']
    manhua_name = input('请输入要搜索的关键字:')
    manhua = parse.quote(manhua_name)
    start_urls = ['https://www.manhuaniu.com/search/?keywords={}'.format(manhua)]

    def regex_html(self, regex, html):
        """正则解析函数"""
        p = re.compile(regex, re.S)
        result_list = p.findall(html)
        return result_list

    def parse(self, response):
        """根据搜索关键字得到所有搜索到的漫画的名称和URL"""
        html = response.text
        regex = '<a class="cover" href="(.*?)" title="(.*?)">'
        # 搜索到的漫画链接列表
        manhua_list = self.regex_html(regex, html)
        if not manhua_list:
            print('没有找到数据')
        for manhua in manhua_list:
            # print(manhua) ('https://www.manhuaniu.com/manhua/10660/', '一人之下')
            manhua_url = manhua[0]
            manhua_name = manhua[1]
            yield scrapy.Request(url=manhua_url,
                                 meta={'manhua_name': manhua_name},
                                 callback=self.get_chapter_parse)

    def get_chapter_parse(self, response):
        """获取漫画所有章节URL和章节目录名称"""
        manhua_name = response.meta['manhua_name']
        html = response.text
        regex = '<li>.*?<a href="(.*?)".*?<span>(.*?)</span>'
        # 章节链接列表
        chapter_list = self.regex_html(regex, html)
        for chapter in chapter_list:
            # print(chapter)
            if chapter[0][-4:] == 'html':
                two_url = 'https://www.manhuaniu.com' + chapter[0]
                chapter_name = chapter[1]
                yield scrapy.Request(url=two_url,
                                     meta={'chapter_name': chapter_name, 'manhua_name': manhua_name},
                                     callback=self.get_img_link)
            else:
                print('没有找到正确的章节链接地址')
                continue

    def get_img_link(self, response):
        """获取漫画章节具体漫画的URL交给item对象"""
        item = OneItem()
        manhua_name = response.meta['manhua_name']
        chapter_name = response.meta['chapter_name']
        html = response.text
        regex = 'var chapterImages = (.*?);var chapterPath'
        url_list = self.regex_html(regex, html)
        # ['["images\\/comic\\/209\\/416829\\/1565325297jFtGQnCL24KqzaQ5.","images\\/comic\\/209\\/416829\\/1565325296j_qHDe21Kj0zzxXK.","images\\/comic\\/209\\/416829\\/1565325296s2UjVnYw5_aD5gYR.","images\\/comic\\/209\\/416829\\/1565325295QILmVFOYGV3hXNTy.","images\\/comic\\/209\\/416829\\/1565325295SwoZhPLcHYi4JZvA.","images\\/comic\\/209\\/416829\\/1565325295KPSLpiveYROZ8fpV.","images\\/comic\\/209\\/416829\\/15653252948HFOXfVBE6xybyk7.","images\\/comic\\/209\\/416829\\/1565325294VqOq4mco_CDbwoeD.","images\\/comic\\/209\\/416829\\/1565325293KNLZjcUCGOlYZTaP.","images\\/comic\\/209\\/416829\\/1565325293iCyuv-pWPMn8ioo2.","images\\/comic\\/209\\/416829\\/1565325292qEIKw5plqK0Wy5lI.","images\\/comic\\/209\\/416829\\/1565325292t3un7tRgBZtjbsFj.","images\\/comic\\/209\\/416829\\/1565325291IP_JX59UOHIggJVF.","images\\/comic\\/209\\/416829\\/1565325291suaaeIMi40cVRNHX.","images\\/comic\\/209\\/416829\\/1565325290fGeJdri93n_HN6vw."]']
        img_url = url_list[0][1:-1].split(',')
        for index, value in enumerate(img_url):
            # print(index,value) 每张漫画图片的下标位置和URL,下标位置用作图片名称
            # 通过\把字符串切割成多部分，去除\
            imgs_name = str(index + 1)
            imgs = value[1:-1].split('\\')
            # 拼接切割出来的部分，组成正确的URL
            imgs_url = ''.join(imgs)
            item['img_link'] = 'https://restp.dongqiniqin.com//' + imgs_url
            item['chapter_name'] = chapter_name
            item['manhua_name'] = manhua_name
            item['img_name'] = imgs_name
            yield item
