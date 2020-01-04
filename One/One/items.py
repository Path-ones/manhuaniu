# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OneItem(scrapy.Item):
    # define the fields for your item here like:
    img_link = scrapy.Field()  # 漫画图片URL
    chapter_name = scrapy.Field()  # 章节目录名称
    manhua_name = scrapy.Field()  # 漫画名称
    img_name = scrapy.Field()  # 图片名称
