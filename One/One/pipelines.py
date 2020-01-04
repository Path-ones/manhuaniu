# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline


class OnePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        print('正在下载:', item['chapter_name'] + '_' + item['img_name'] + '.jpg')
        yield scrapy.Request(url=item['img_link'],
                             meta={'name': item['img_name'],
                                   'manhua_name': item['manhua_name'],
                                   'chapter_name': item['chapter_name']})

    def file_path(self, request, response=None, info=None):
        # name = parse.unquote(request.meta['name']).encode('utf8')
        filename = '/%s/%s/%s' % (
            request.meta['manhua_name'], request.meta['chapter_name'], request.meta['name'] + '.jpg')
        return filename
