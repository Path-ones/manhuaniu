# -*- coding: utf-8 -*-
import re
import scrapy
from urllib import parse
from ..items import OneItem


class OneSpider(scrapy.Spider):
    name = 'one'
    allowed_domains = ['www.manhuaniu.com']
    try:
        manhua_name = input('请输入漫画名称关键字:')
        manhua = parse.quote(manhua_name)
        start_urls = ['https://www.manhuaniu.com/search/?keywords={}'.format(manhua)]
    except KeyboardInterrupt:
        print()
        print('手动结束')

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
        # 如果没有漫画,则列表为空
        if not manhua_list:
            print('没有找到数据')
        else:
            all_dict = {}
            for index, manhua in enumerate(manhua_list):
                # print(manhua) ('https://www.manhuaniu.com/manhua/10660/', '一人之下')
                # 把列表的索引和值存入字典
                all_dict[index] = manhua
            # 显示所有搜索到的漫画名称
            print('*' * 40)
            print('请根据搜索到的漫画编号和名称选择需要下载的漫画')
            print('*' * 40)
            print('编号     名称')
            print('*' * 40)
            # 定义一个新列表并指向漫画列表
            a_list = manhua_list
            # 遍历新列表,将搜索到的漫画和编号打印在终端,便于选择需要下载的漫画
            for index, value in enumerate(a_list):
                print(index, value[1])
            print('*' * 40)
            try:
                # 输入编号,把编号作为key查找对应的漫画
                num = int(input('请选择要下载的漫画编号:'))
                manhua_url = all_dict[num][0]  # 漫画URL
                manhua_name = all_dict[num][1]  # 漫画名称
                yield scrapy.Request(url=manhua_url,
                                     meta={'manhua_name': manhua_name},
                                     callback=self.get_chapter_parse)
            except:
                print('请输入正确的数字编号')

    def get_chapter_parse(self, response):
        """获取漫画所有章节URL和章节目录名称"""
        # 漫画名称
        manhua_name = response.meta['manhua_name']
        html = response.text
        regex = '<li>.*?<a href="(.*?)".*?<span>(.*?)</span>'
        # 章节链接列表
        chapter_list = self.regex_html(regex, html)
        for chapter in chapter_list:
            # print(chapter)
            if chapter[0][-4:] == 'html':
                two_url = 'https://www.manhuaniu.com' + chapter[0]
                chapter_name = chapter[1]  # 章节名称
                yield scrapy.Request(url=two_url,
                                     meta={'chapter_name': chapter_name, 'manhua_name': manhua_name},
                                     callback=self.get_img_link)
            else:
                print('没有找到正确的章节链接地址')
                continue

    def get_img_link(self, response):
        """获取漫画章节具体漫画的URL交给item对象"""
        item = OneItem()
        manhua_name = response.meta['manhua_name']  # 漫画名称
        chapter_name = response.meta['chapter_name']  # 章节名称
        html = response.text
        regex = 'var chapterImages = (.*?);var chapterPath'
        # 每一章所有页漫画的URL列表 ['["","","",...]'] 列表其实只有一个元素,''里面的都是字符串,包括[]
        url_list = self.regex_html(regex, html)
        # ['["images\\/comic\\/209\\/416829\\/1565325297jFtGQnCL24KqzaQ5.","images\\/comic\\/209\\/416829\\/1565325296j_qHDe21Kj0zzxXK.",..."]']
        # 通过[0],取到唯一的一个元素,然后用[1:-1]切片去除字符串开头结尾的[]两个符号,再用','符号切割,分成多个URL并形成列表
        img_url = url_list[0][1:-1].split(',')
        for index, value in enumerate(img_url):
            # print(index,value) 每张漫画图片的下标位置和URL,下标位置用作图片名称
            imgs_name = str(index + 1)
            # 把value字符串开头结尾的""两个符号去除并通过\符号切割,去除\符号
            imgs = value[1:-1].split('\\')  # \符号由于有特殊含义,需要在前面加\转义
            # 用空字符串拼接切割出来的部分，组成正确的URL
            imgs_url = ''.join(imgs)
            item['img_link'] = 'https://restp.dongqiniqin.com//' + imgs_url
            item['chapter_name'] = chapter_name
            item['manhua_name'] = manhua_name
            item['img_name'] = imgs_name
            yield item
