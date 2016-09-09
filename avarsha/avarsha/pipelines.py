# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import os.path
import rfc822
import time
import json
from cStringIO import StringIO
from PIL import Image
from sets import Set
from twisted.internet import defer

from scrapy.http import Request
from scrapy import log
from scrapy.contrib.pipeline.files import S3FilesStore
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from boto.dynamodb2.exceptions import ItemNotFound

from avarsha.dynamo_db import DynamoDB
from openpyxl import load_workbook


class AvarshaPipeline(object):
    def __init__(self):
        self.dynamo_db = DynamoDB()

    def __build_product_availabity_item(self, product_item):
        if (product_item.get('colors') is None
            and product_item.get('sizes') is None
            and product_item.get('stocks') is None):
            return None

        pa_item = {}
        pa_item['product_id'] = product_item['product_id']
        if product_item.get('colors') != None:
            pa_item['colors'] = product_item['colors']
        if product_item.get('sizes') != None:
            pa_item['sizes'] = product_item['sizes']
        if product_item.get('stocks') != None:
            pa_item['stocks'] = product_item['stocks']
        pa_item['crawl_datetime'] = product_item['crawl_datetime']
        return pa_item

    def __build_product_sales_item(self, product_item):
        if (product_item.get('list_price') is None
            and product_item.get('price') is None
            and product_item.get('low_price') is None
            and product_item.get('high_price') is None
            and product_item.get('free_shipping') is None):
            return None

        ps_item = {}
        ps_item['product_id'] = product_item['product_id']
        if product_item.get('list_price') != None:
            ps_item['list_price'] = product_item['list_price']
        if product_item.get('price') != None:
            ps_item['price'] = product_item['price']
        if product_item.get('low_price') != None:
            ps_item['low_price'] = product_item['low_price']
        if product_item.get('high_price') != None:
            ps_item['high_price'] = product_item['high_price']
        if product_item.get('free_shipping') != None:
            ps_item['free_shipping'] = product_item['free_shipping']
        ps_item['crawl_datetime'] = product_item['crawl_datetime']
        return ps_item

    def __build_product_reviews_item(self, product_item):
        if (product_item.get('review_count') is None
            and product_item.get('max_review_rating') is None
            and product_item.get('review_rating') is None
            and product_item.get('review_list') is None):
            return None

        pr_item = {}
        pr_item['product_id'] = product_item['product_id']
        if product_item.get('review_count') != None:
            pr_item['review_count'] = product_item['review_count']
        if product_item.get('max_review_rating') != None:
            pr_item['max_review_rating'] = product_item['max_review_rating']
        if product_item.get('review_rating') != None:
            pr_item['review_rating'] = product_item['review_rating']
        if product_item.get('review_list') != None:
            pr_item['review_list'] = product_item['review_list']
        pr_item['crawl_datetime'] = product_item['crawl_datetime']
        return pr_item

    def process_item(self, item, spider):
#         if item.normalize_attributes() is False:
#             raise DropItem("Attributes format error in %s" % item)
#         self.__assert_necessary_attributes(item)

        if spider.settings['VERSION'] == 'DEV':
            #self.store(item)
            return item

        if spider.settings['CHROME_ENABLED'] is True:
            try:
                chrome_item = self.dynamo_db.table('chrome').get_item(url=item['url'])
                item['chrome_clicks'] = chrome_item['clicks']
            except ItemNotFound:
                log.msg('URL not in chrome log: %s' % item['url'] , log.DEBUG)

        product_id = item.get('product_id')
        old_item = None
        try:
            old_item = self.dynamo_db.table('products').get_item(product_id=product_id)
            item['collections'] = list(item['collections'])
            if old_item != item:
                item['updated_datetime'] = item['crawl_datetime']
                log.msg('Item updated since last crawl: %s' % product_id, log.DEBUG)
            else:
                # detect if it is crawled recently
                old_item['crawl_datetime'] = item['crawl_datetime']
                old_item.partial_save()
                log.msg('Item not changed: %s' % product_id, log.DEBUG)
                return item
        except ItemNotFound:
            log.msg('Find a new item: %s' % product_id, log.DEBUG)
            item['updated_datetime'] = item['crawl_datetime']

        # merge current collections to previous collections
        if old_item != None:
            new_collections = Set(old_item.get('collections')) \
                | Set(item.get('collections'))
        else:
            new_collections = Set(item.get('collections'))
        if len(new_collections) != 0:
            item['collections'] = list(new_collections)

        log.msg('Save item info to Dynamo DB: %s' % product_id, log.DEBUG)

        self.dynamo_db.table('products').put_item(data=item, overwrite=True)

        pa_item = self.__build_product_availabity_item(item)
        if pa_item != None:
            self.dynamo_db.table('product_availabity')\
                .put_item(data=pa_item, overwrite=True)

        ps_item = self.__build_product_sales_item(item)
        if ps_item != None:
            self.dynamo_db.table('product_sales')\
                .put_item(data=ps_item, overwrite=True)

        pr_item = self.__build_product_reviews_item(item)
        if pr_item != None:
            self.dynamo_db.table('product_reviews')\
                .put_item(data=pr_item, overwrite=True)

        return item

    def open_spider(self, spider):
        feeder = spider.feeder

        if spider.settings['VERSION'] == 'DEV':
            # for test for spider
#             start_urls = []
#             wb = load_workbook('D:/www/dev-web-crawler/products_url.xlsx')
#             ws = wb.active
#             for i in range(1,490):
#                 start_urls.append(ws.cell(row = i,column = 1).value)
#             wb.save('D:/www/dev-web-crawler/products_url.xlsx')

            start_urls = [
                            'https://detail.1688.com/offer/1284633110.html?sitename=accessory&sku=SP_800001',
                            'https://detail.1688.com/offer/1282109178.html?sitename=accessory&sku=SP_800002',
                            'https://detail.1688.com/offer/1217927003.html?sitename=accessory&sku=SP_800003',
                            'https://detail.1688.com/offer/532898607208.html?sitename=accessory&sku=SP_800004',
                            'https://detail.1688.com/offer/535007648172.html?sitename=accessory&sku=SP_800005',
                            'https://detail.1688.com/offer/535005912659.html?sitename=accessory&sku=SP_800006',
                            'https://detail.1688.com/offer/536173263085.html?sitename=accessory&sku=SP_800007',
                            'https://detail.1688.com/offer/533000643566.html?sitename=accessory&sku=SP_800008',
                            'https://detail.1688.com/offer/45535341899.html?sitename=accessory&sku=SP_800009',
                            'https://detail.1688.com/offer/526377951832.html?sitename=accessory&sku=SP_800010',
                            'https://detail.1688.com/offer/537362460812.html?sitename=accessory&sku=SP_800011',
                            'https://detail.1688.com/offer/521500995980.html?sitename=accessory&sku=SP_800012',
                            'https://detail.1688.com/offer/1285216925.html?sitename=accessory&sku=SP_800013',
                            'https://detail.1688.com/offer/42586811918.html?sitename=accessory&sku=SP_800014',
                            'https://detail.1688.com/offer/41197045039.html?sitename=accessory&sku=SP_800015',
                            'https://detail.1688.com/offer/41155547502.html?sitename=accessory&sku=SP_800016',
                            'https://detail.1688.com/offer/1002563777.html?sitename=accessory&sku=SP_800017',
                            'https://detail.1688.com/offer/536638928650.html?sitename=accessory&sku=SP_800018',
                            'https://detail.1688.com/offer/536847697614.html?sitename=accessory&sku=SP_800019',
                            'https://detail.1688.com/offer/531333220721.html?sitename=accessory&sku=SP_800020',
                            'https://detail.1688.com/offer/534858785958.html?sitename=accessory&sku=SP_800021',
                            'https://detail.1688.com/offer/524226273758.html?sitename=accessory&sku=SP_800022',
                            'https://detail.1688.com/offer/42088819467.html?sitename=accessory&sku=SP_800023',
                            'https://detail.1688.com/offer/522172672301.html?sitename=accessory&sku=SP_800024',
                            'https://detail.1688.com/offer/537081002349.html?sitename=accessory&sku=SP_800025',
                            'https://detail.1688.com/offer/43125024149.html?sitename=accessory&sku=SP_800026',
                            'https://detail.1688.com/offer/521468524688.html?sitename=accessory&sku=SP_800027',
                            'https://detail.1688.com/offer/523899159456.html?sitename=accessory&sku=SP_800028',
                            'https://detail.1688.com/offer/534196298005.html?sitename=accessory&sku=SP_800029',
                            'https://detail.1688.com/offer/528953093817.html?sitename=accessory&sku=SP_800030',
                            'https://detail.1688.com/offer/533907299768.html?sitename=accessory&sku=SP_800031',
                            'https://detail.1688.com/offer/522990046293.html?sitename=accessory&sku=SP_800032',
                            'https://detail.1688.com/offer/525196668733.html?sitename=accessory&sku=SP_800033',
                            'https://detail.1688.com/offer/521100448481.html?sitename=accessory&sku=SP_800034',
                            'https://detail.1688.com/offer/37382463937.html?sitename=accessory&sku=SP_800035',
                            'https://detail.1688.com/offer/528177663850.html?sitename=accessory&sku=SP_800036',
                            'https://detail.1688.com/offer/528694077078.html?sitename=accessory&sku=SP_800037',
                            'https://detail.1688.com/offer/528489341677.html?sitename=accessory&sku=SP_800038',
                            'https://detail.1688.com/offer/528990487673.html?sitename=accessory&sku=SP_800039',
                            'https://detail.1688.com/offer/536560314167.html?sitename=accessory&sku=SP_800040',
                            'https://detail.1688.com/offer/528343784878.html?sitename=accessory&sku=SP_800041',
                            'https://detail.1688.com/offer/534332541428.html?sitename=accessory&sku=SP_800042',
                            'https://detail.1688.com/offer/534520189074.html?sitename=accessory&sku=SP_800043',
                            'https://detail.1688.com/offer/522743365178.html?sitename=accessory&sku=SP_800044',
                            'https://detail.1688.com/offer/535912563042.html?sitename=accessory&sku=SP_800045',
                            'https://detail.1688.com/offer/535556957211.html?sitename=accessory&sku=SP_800046',
                            'https://detail.1688.com/offer/531462577538.html?sitename=accessory&sku=SP_800047',
                            'https://detail.1688.com/offer/531061019318.html?sitename=accessory&sku=SP_800048',
                            'https://detail.1688.com/offer/531136693599.html?sitename=accessory&sku=SP_800049',
                            'https://detail.1688.com/offer/526540609649.html?sitename=accessory&sku=SP_800050',
                            'https://detail.1688.com/offer/530904779788.html?sitename=accessory&sku=SP_800051',
                            'https://detail.1688.com/offer/529334391561.html?sitename=accessory&sku=SP_800052',
                            'https://detail.1688.com/offer/526542515357.html?sitename=accessory&sku=SP_800053',
                            'https://detail.1688.com/offer/525242981487.html?sitename=accessory&sku=SP_800054',
                            'https://detail.1688.com/offer/532909636765.html?sitename=accessory&sku=SP_800055',
                            'https://detail.1688.com/offer/532109559899.html?sitename=accessory&sku=SP_800056',
                            'https://detail.1688.com/offer/45277300520.html?sitename=accessory&sku=SP_800057',
                            'https://detail.1688.com/offer/45259077531.html?sitename=accessory&sku=SP_800058',
                            'https://detail.1688.com/offer/525630869074.html?sitename=accessory&sku=SP_800059',
                            'https://detail.1688.com/offer/41043329624.html?sitename=accessory&sku=SP_800060',
                            'https://detail.1688.com/offer/41043329624.html?sitename=accessory&sku=SP_800061',
                            'https://detail.1688.com/offer/522000410028.html?sitename=accessory&sku=SP_800062',
                            'https://detail.1688.com/offer/537268582810.html?sitename=accessory&sku=SP_800063',
                            'https://detail.1688.com/offer/531279430018.html?sitename=accessory&sku=SP_800064',
                            'https://detail.1688.com/offer/533045787733.html?sitename=accessory&sku=SP_800065',
                            'https://detail.1688.com/offer/523079268831.html?sitename=accessory&sku=SP_800066',
                            'https://detail.1688.com/offer/528492717558.html?sitename=accessory&sku=SP_800067',
                            'https://detail.1688.com/offer/1291386095.html?sitename=accessory&sku=SP_800068',
                            'https://detail.1688.com/offer/530720285363.html?sitename=accessory&sku=SP_800069',
                            'https://detail.1688.com/offer/533174852806.html?sitename=accessory&sku=SP_800070',
                            'https://detail.1688.com/offer/533176096342.html?sitename=accessory&sku=SP_800071',
                            'https://detail.1688.com/offer/533116526122.html?sitename=accessory&sku=SP_800072',
                            'https://detail.1688.com/offer/533200930738.html?sitename=accessory&sku=SP_800073',
                            'https://detail.1688.com/offer/521209930430.html?sitename=accessory&sku=SP_800074',
                            'https://detail.1688.com/offer/525025238794.html?sitename=accessory&sku=SP_800075',
                            'https://detail.1688.com/offer/537226904654.html?sitename=accessory&sku=SP_800076',
                            'https://detail.1688.com/offer/537977445649.html?sitename=accessory&sku=SP_800077',
                            'https://detail.1688.com/offer/38375182324.html?sitename=accessory&sku=SP_800078',
                            'https://detail.1688.com/offer/532839707883.html?sitename=accessory&sku=SP_800079',
                            'https://detail.1688.com/offer/536021323252.html?sitename=accessory&sku=SP_800080',
                            'https://detail.1688.com/offer/531733497187.html?sitename=accessory&sku=SP_800081',
                            'https://detail.1688.com/offer/525507657178.html?sitename=accessory&sku=SP_800082',
                            'https://detail.1688.com/offer/521048713260.html?sitename=accessory&sku=SP_800083',
                            'https://detail.1688.com/offer/535495835047.html?sitename=accessory&sku=SP_800084',
                            'https://detail.1688.com/offer/45651187075.html?sitename=accessory&sku=SP_800085',
                            'https://detail.1688.com/offer/520974970020.html?sitename=accessory&sku=SP_800086',
                            'https://detail.1688.com/offer/522660211764.html?sitename=accessory&sku=SP_800087',
                            'https://detail.1688.com/offer/522599833933.html?sitename=accessory&sku=SP_800088',
                            'https://detail.1688.com/offer/526062212828.html?sitename=accessory&sku=SP_800089',
                            'https://detail.1688.com/offer/531827162108.html?sitename=accessory&sku=SP_800090',
                            'https://detail.1688.com/offer/537311477163.html?sitename=accessory&sku=SP_800091',
                            'https://detail.1688.com/offer/40546767334.html?sitename=accessory&sku=SP_800092',
                            'https://detail.1688.com/offer/525890243000.html?sitename=accessory&sku=SP_800093',
                            'https://detail.1688.com/offer/536819362845.html?sitename=accessory&sku=SP_800094',
                            'https://detail.1688.com/offer/521664826735.html?sitename=accessory&sku=SP_800095',
                            'https://detail.1688.com/offer/1275954842.html?sitename=accessory&sku=SP_800096',
                            'https://detail.1688.com/offer/42569285351.html?sitename=accessory&sku=SP_800097',
                            'https://detail.1688.com/offer/530764806051.html?sitename=accessory&sku=SP_800098',
                            'https://detail.1688.com/offer/533212222378.html?sitename=accessory&sku=SP_800099',
                            'https://detail.1688.com/offer/527378026982.html?sitename=accessory&sku=SP_800100',
                            'https://detail.1688.com/offer/535947538908.html?sitename=accessory&sku=SP_800101',
                            'https://detail.1688.com/offer/535543584091.html?sitename=accessory&sku=SP_800102',
                            'https://detail.1688.com/offer/530701105722.html?sitename=accessory&sku=SP_800103',
                            'https://detail.1688.com/offer/534786070159.html?sitename=accessory&sku=SP_800104',
                            'https://detail.1688.com/offer/35757956111.html?sitename=accessory&sku=SP_800105',
                            'https://detail.1688.com/offer/35792124067.html?sitename=accessory&sku=SP_800106',
                            'https://detail.1688.com/offer/35709399117.html?sitename=accessory&sku=SP_800107',
                            'https://detail.1688.com/offer/42217804940.html?sitename=accessory&sku=SP_800108',
                            'https://detail.1688.com/offer/530745981715.html?sitename=accessory&sku=SP_800109',
                            'https://detail.1688.com/offer/530771920337.html?sitename=accessory&sku=SP_800110',
                            'https://detail.1688.com/offer/530469359893.html?sitename=accessory&sku=SP_800111',
                            'https://detail.1688.com/offer/534040025369.html?sitename=accessory&sku=SP_800112',
                            'https://detail.1688.com/offer/536104772958.html?sitename=accessory&sku=SP_800113',
                            'https://detail.1688.com/offer/520986458309.html?sitename=accessory&sku=SP_800114',
                            'https://detail.1688.com/offer/1213932919.html?sitename=accessory&sku=SP_800115',
                            'https://detail.1688.com/offer/45361503569.html?sitename=accessory&sku=SP_800116',
                            'https://detail.1688.com/offer/35833826068.html?sitename=accessory&sku=SP_800117',
                            'https://detail.1688.com/offer/36490326097.html?sitename=accessory&sku=SP_800118',
                            'https://detail.1688.com/offer/36993676935.html?sitename=accessory&sku=SP_800119',
                            'https://detail.1688.com/offer/35674688924.html?sitename=accessory&sku=SP_800120',
                            'https://detail.1688.com/offer/35645645239.html?sitename=accessory&sku=SP_800121',
                            'https://detail.1688.com/offer/36799426033.html?sitename=accessory&sku=SP_800122',
                            'https://detail.1688.com/offer/39255151376.html?sitename=accessory&sku=SP_800123',
                            'https://detail.1688.com/offer/36885988437.html?sitename=accessory&sku=SP_800124',
                            'https://detail.1688.com/offer/35710721539.html?sitename=accessory&sku=SP_800125',
                            'https://detail.1688.com/offer/35715863999.html?sitename=accessory&sku=SP_800126',
                            'https://detail.1688.com/offer/45538891589.html?sitename=accessory&sku=SP_800127',
                            'https://detail.1688.com/offer/524751969823.html?sitename=accessory&sku=SP_800128',
                            'https://detail.1688.com/offer/524157026165.html?sitename=accessory&sku=SP_800129',
                            'https://detail.1688.com/offer/524039040720.html?sitename=accessory&sku=SP_800130',
                            'https://detail.1688.com/offer/521096422835.html?sitename=accessory&sku=SP_800131',
                            'https://detail.1688.com/offer/44175582992.html?sitename=accessory&sku=SP_800132',
                            'https://detail.1688.com/offer/44013662229.html?sitename=accessory&sku=SP_800133',
                            'https://detail.1688.com/offer/524631614037.html?sitename=accessory&sku=SP_800134',
                            'https://detail.1688.com/offer/522991617095.html?sitename=accessory&sku=SP_800135',
                            'https://detail.1688.com/offer/520185610432.html?sitename=accessory&sku=SP_800136',
                            'https://detail.1688.com/offer/528854234085.html?sitename=accessory&sku=SP_800137',
                            'https://detail.1688.com/offer/529341646432.html?sitename=accessory&sku=SP_800138',
                            'https://detail.1688.com/offer/529381816126.html?sitename=accessory&sku=SP_800139',
                            'https://detail.1688.com/offer/964845683.html?sitename=accessory&sku=SP_800140',
                            'https://detail.1688.com/offer/529381360172.html?sitename=accessory&sku=SP_800141',
                            'https://detail.1688.com/offer/531063623001.html?sitename=accessory&sku=SP_800142',
                            'https://detail.1688.com/offer/528436705774.html?sitename=accessory&sku=SP_800143',
                            'https://detail.1688.com/offer/1175176903.html?sitename=accessory&sku=SP_800144',
                            'https://detail.1688.com/offer/976153272.html?sitename=accessory&sku=SP_800145',
                            'https://detail.1688.com/offer/530151891948.html?sitename=accessory&sku=SP_800146',
                            'https://detail.1688.com/offer/39783681768.html?sitename=accessory&sku=SP_800147',
                            'https://detail.1688.com/offer/536695335558.html?sitename=accessory&sku=SP_800148',
                            'https://detail.1688.com/offer/520247697810.html?sitename=accessory&sku=SP_800149',
                            'https://detail.1688.com/offer/525871011965.html?sitename=accessory&sku=SP_800150',
                            'https://detail.1688.com/offer/43936638224.html?sitename=accessory&sku=SP_800151',
                            'https://detail.1688.com/offer/536695175628.html?sitename=accessory&sku=SP_800152',
                            'https://detail.1688.com/offer/41740290606.html?sitename=accessory&sku=SP_800153',
                            'https://detail.1688.com/offer/525871011968.html?sitename=accessory&sku=SP_800154',
                            'https://detail.1688.com/offer/530177463231.html?sitename=accessory&sku=SP_800155',
                            'https://detail.1688.com/offer/42775065633.html?sitename=accessory&sku=SP_800156',
                            'https://detail.1688.com/offer/536987241535.html?sitename=accessory&sku=SP_800157',
                            'https://detail.1688.com/offer/535732185074.html?sitename=accessory&sku=SP_800158',
                            'https://detail.1688.com/offer/43368009741.html?sitename=accessory&sku=SP_800159',
                            'https://detail.1688.com/offer/521518928868.html?sitename=accessory&sku=SP_800160',
                            'https://detail.1688.com/offer/536933869378.html?sitename=accessory&sku=SP_800161',
                            'https://detail.1688.com/offer/520058043833.html?sitename=accessory&sku=SP_800162',
                            'https://detail.1688.com/offer/535891400501.html?sitename=accessory&sku=SP_800163',
                            'https://detail.1688.com/offer/43915518514.html?sitename=accessory&sku=SP_800164',
                            'https://detail.1688.com/offer/530159518342.html?sitename=accessory&sku=SP_800165',
                            'https://detail.1688.com/offer/528376169618.html?sitename=accessory&sku=SP_800166',
                            'https://detail.1688.com/offer/528375541673.html?sitename=accessory&sku=SP_800167',
                            'https://detail.1688.com/offer/528358862020.html?sitename=accessory&sku=SP_800168',
                            'https://detail.1688.com/offer/528371441221.html?sitename=accessory&sku=SP_800169',
                            'https://detail.1688.com/offer/528391592465.html?sitename=accessory&sku=SP_800170',
                            'https://detail.1688.com/offer/528396228352.html?sitename=accessory&sku=SP_800171',
                            'https://detail.1688.com/offer/528391453906.html?sitename=accessory&sku=SP_800172',
                            'https://detail.1688.com/offer/528362038805.html?sitename=accessory&sku=SP_800173',
                            'https://detail.1688.com/offer/528396760106.html?sitename=accessory&sku=SP_800174',
                            'https://detail.1688.com/offer/528367712512.html?sitename=accessory&sku=SP_800175',
                            'https://detail.1688.com/offer/528367840934.html?sitename=accessory&sku=SP_800176',
                            'https://detail.1688.com/offer/528379589620.html?sitename=accessory&sku=SP_800177',
                            'https://detail.1688.com/offer/44638220898.html?sitename=accessory&sku=SP_800178',
                            'https://detail.1688.com/offer/44009954460.html?sitename=accessory&sku=SP_800179',
                            'https://detail.1688.com/offer/520411969307.html?sitename=accessory&sku=SP_800180',
                            'https://detail.1688.com/offer/520415476200.html?sitename=accessory&sku=SP_800181',
                            'https://detail.1688.com/offer/39891217947.html?sitename=accessory&sku=SP_800182',
                            'https://detail.1688.com/offer/535441282025.html?sitename=accessory&sku=SP_800183',
                            'https://detail.1688.com/offer/43367771973.html?sitename=accessory&sku=SP_800184',
                            'https://detail.1688.com/offer/37511359615.html?sitename=accessory&sku=SP_800185',
                            'https://detail.1688.com/offer/525472925568.html?sitename=accessory&sku=SP_800186',
                            'https://detail.1688.com/offer/524030208470.html?sitename=accessory&sku=SP_800187',
                            'https://detail.1688.com/offer/36130035932.html?sitename=accessory&sku=SP_800188',
                            'https://detail.1688.com/offer/1282109178.html?sitename=accessory&sku=SP_800189',
                            'https://detail.1688.com/offer/1214381296.html?sitename=accessory&sku=SP_800190',
                            'https://detail.1688.com/offer/538119637625.html?sitename=accessory&sku=SP_800191',
                            'https://detail.1688.com/offer/537507536906.html?sitename=accessory&sku=SP_800192',
                            'https://detail.1688.com/offer/537471685259.html?sitename=accessory&sku=SP_800193',
                            'https://detail.1688.com/offer/1284633110.html?sitename=accessory&sku=SP_800194',
                            'https://detail.1688.com/offer/538071908817.html?sitename=accessory&sku=SP_800195',
                            'https://detail.1688.com/offer/1219057090.html?sitename=accessory&sku=SP_800196',
                            'https://detail.1688.com/offer/530172005054.html?sitename=accessory&sku=SP_800197',
                            'https://detail.1688.com/offer/527253650560.html?sitename=accessory&sku=SP_800198',
                            'https://detail.1688.com/offer/526366872240.html?sitename=accessory&sku=SP_800199',
                            'https://detail.1688.com/offer/532769177441.html?sitename=accessory&sku=SP_800200',
                            'https://detail.1688.com/offer/534993732148.html?sitename=accessory&sku=SP_800201',
                            'https://detail.1688.com/offer/534296207375.html?sitename=accessory&sku=SP_800202',
                            'https://detail.1688.com/offer/45800954231.html?sitename=accessory&sku=SP_800203',
                            'https://detail.1688.com/offer/41635099561.html?sitename=accessory&sku=SP_800204',
                            'https://detail.1688.com/offer/41223512231.html?sitename=accessory&sku=SP_800205',
                            'https://detail.1688.com/offer/41680821550.html?sitename=accessory&sku=SP_800206',
                            'https://detail.1688.com/offer/1183423150.html?sitename=accessory&sku=SP_800207',
                            'https://detail.1688.com/offer/528239861295.html?sitename=accessory&sku=SP_800208',
                            'https://detail.1688.com/offer/524169122572.html?sitename=accessory&sku=SP_800209',
                            'https://detail.1688.com/offer/528251449126.html?sitename=accessory&sku=SP_800210',
                            'https://detail.1688.com/offer/42007714849.html?sitename=accessory&sku=SP_800211',
                            'https://detail.1688.com/offer/520735636616.html?sitename=accessory&sku=SP_800212',
                            'https://detail.1688.com/offer/42008106392.html?sitename=accessory&sku=SP_800213',
                            'https://detail.1688.com/offer/41988835779.html?sitename=accessory&sku=SP_800214',
                            'https://detail.1688.com/offer/41988835779.html?sitename=accessory&sku=SP_800215',
                            'https://detail.1688.com/offer/44599539566.html?sitename=accessory&sku=SP_800216',
                            'https://detail.1688.com/offer/1203501493.html?sitename=accessory&sku=SP_800217',
                            'https://detail.1688.com/offer/38373906783.html?sitename=accessory&sku=SP_800218',
                            'https://detail.1688.com/offer/520933519321.html?sitename=accessory&sku=SP_800219',
                            'https://detail.1688.com/offer/1255344088.html?sitename=accessory&sku=SP_800220',
                            'https://detail.1688.com/offer/44599603650.html?sitename=accessory&sku=SP_800221',
                            'https://detail.1688.com/offer/37617179942.html?sitename=accessory&sku=SP_800222',
                            'https://detail.1688.com/offer/37717750472.html?sitename=accessory&sku=SP_800223',
                            'https://detail.1688.com/offer/1175051156.html?sitename=accessory&sku=SP_800224',
                            'https://detail.1688.com/offer/1186843168.html?sitename=accessory&sku=SP_800225',
                            'https://detail.1688.com/offer/44259526881.html?sitename=accessory&sku=SP_800226',
                            'https://detail.1688.com/offer/38356575641.html?sitename=accessory&sku=SP_800227',
                            'https://detail.1688.com/offer/1218495719.html?sitename=accessory&sku=SP_800228',
                            'https://detail.1688.com/offer/36567939823.html?sitename=accessory&sku=SP_800229',
                            'https://detail.1688.com/offer/44236647792.html?sitename=accessory&sku=SP_800230',
                            'https://detail.1688.com/offer/1263268089.html?sitename=accessory&sku=SP_800231',
                            'https://detail.1688.com/offer/530856957148.html?sitename=accessory&sku=SP_800232',
                            'https://detail.1688.com/offer/520739128587.html?sitename=accessory&sku=SP_800233',
                            'https://detail.1688.com/offer/520732480045.html?sitename=accessory&sku=SP_800234',
                            'https://detail.1688.com/offer/1219736697.html?sitename=accessory&sku=SP_800235',
                            'https://detail.1688.com/offer/1175139302.html?sitename=accessory&sku=SP_800236',
                            'https://detail.1688.com/offer/36266219529.html?sitename=accessory&sku=SP_800237',
                            'https://detail.1688.com/offer/36551354933.html?sitename=accessory&sku=SP_800238',
                            'https://detail.1688.com/offer/36563368363.html?sitename=accessory&sku=SP_800239',
                            'https://detail.1688.com/offer/45589969489.html?sitename=accessory&sku=SP_800240',
                            'https://detail.1688.com/offer/45040575997.html?sitename=accessory&sku=SP_800241',
                            'https://detail.1688.com/offer/1258521901.html?sitename=accessory&sku=SP_800242',
                            'https://detail.1688.com/offer/520719808568.html?sitename=accessory&sku=SP_800243',
                            'https://detail.1688.com/offer/39967088365.html?sitename=accessory&sku=SP_800244',
                            'https://detail.1688.com/offer/38578824907.html?sitename=accessory&sku=SP_800245',
                            'https://detail.1688.com/offer/520899904860.html?sitename=accessory&sku=SP_800246',
                            'https://detail.1688.com/offer/520571026991.html?sitename=accessory&sku=SP_800247',
                            'https://detail.1688.com/offer/45853209530.html?sitename=accessory&sku=SP_800248',
                            'https://detail.1688.com/offer/521673927968.html?sitename=accessory&sku=SP_800249',
                            'https://detail.1688.com/offer/523325586722.html?sitename=accessory&sku=SP_800250',
                            'https://detail.1688.com/offer/44290671480.html?sitename=accessory&sku=SP_800251',
                            'https://detail.1688.com/offer/521824618221.html?sitename=accessory&sku=SP_800252',
                            'https://detail.1688.com/offer/521672467603.html?sitename=accessory&sku=SP_800253',
                            'https://detail.1688.com/offer/520598340880.html?sitename=accessory&sku=SP_800254',
                            'https://detail.1688.com/offer/520573368246.html?sitename=accessory&sku=SP_800255',
                            'https://detail.1688.com/offer/39461895794.html?sitename=accessory&sku=SP_800256',
                            'https://detail.1688.com/offer/43401453689.html?sitename=accessory&sku=SP_800257',
                            'https://detail.1688.com/offer/41459092919.html?sitename=accessory&sku=SP_800258',
                            'https://detail.1688.com/offer/35687325105.html?sitename=accessory&sku=SP_800259',
                            'https://detail.1688.com/offer/37392160880.html?sitename=accessory&sku=SP_800260',
                            'https://detail.1688.com/offer/36334947464.html?sitename=accessory&sku=SP_800261',
                            'https://detail.1688.com/offer/36265977350.html?sitename=accessory&sku=SP_800262',
                            'https://detail.1688.com/offer/38984112662.html?sitename=accessory&sku=SP_800263',
                            'https://detail.1688.com/offer/527261641746.html?sitename=accessory&sku=SP_800264',
                            'https://detail.1688.com/offer/520710019899.html?sitename=accessory&sku=SP_800265',
                            'https://detail.1688.com/offer/520569131647.html?sitename=accessory&sku=SP_800266',
                            'https://detail.1688.com/offer/45592285100.html?sitename=accessory&sku=SP_800267',
                            'https://detail.1688.com/offer/36474719260.html?sitename=accessory&sku=SP_800268',
                            'https://detail.1688.com/offer/520549197860.html?sitename=accessory&sku=SP_800269',
                            'https://detail.1688.com/offer/525754353802.html?sitename=accessory&sku=SP_800270',
                            'https://detail.1688.com/offer/532893090304.html?sitename=accessory&sku=SP_800271',
                            'https://detail.1688.com/offer/524429139158.html?sitename=accessory&sku=SP_800272',
                            'https://detail.1688.com/offer/520555792891.html?sitename=accessory&sku=SP_800273',
                            'https://detail.1688.com/offer/527470193194.html?sitename=accessory&sku=SP_800274',
                            'https://detail.1688.com/offer/525072099247.html?sitename=accessory&sku=SP_800275',
                            'https://detail.1688.com/offer/40350360855.html?sitename=accessory&sku=SP_800276',
                            'https://detail.1688.com/offer/42623029997.html?sitename=accessory&sku=SP_800277',
                            'https://detail.1688.com/offer/42717511894.html?sitename=accessory&sku=SP_800278',
                            'https://detail.1688.com/offer/526168860157.html?sitename=accessory&sku=SP_800279',
                            'https://detail.1688.com/offer/525289818217.html?sitename=accessory&sku=SP_800280',
                            'https://detail.1688.com/offer/45655302370.html?sitename=accessory&sku=SP_800281',
                            'https://detail.1688.com/offer/525026873477.html?sitename=accessory&sku=SP_800282',
                            'https://detail.1688.com/offer/526029251886.html?sitename=accessory&sku=SP_800283',
                            'https://detail.1688.com/offer/526062212828.html?sitename=accessory&sku=SP_800284',
                            'https://detail.1688.com/offer/526055468991.html?sitename=accessory&sku=SP_800285',
                            'https://detail.1688.com/offer/537966686143.html?sitename=accessory&sku=SP_800286',
                            'https://detail.1688.com/offer/536984457335.html?sitename=accessory&sku=SP_800287',
                            'https://detail.1688.com/offer/42917038873.html?sitename=accessory&sku=SP_800288',
                            'https://detail.1688.com/offer/522599833933.html?sitename=accessory&sku=SP_800289',
                            'https://detail.1688.com/offer/533976952269.html?sitename=accessory&sku=SP_800290',
                            'https://detail.1688.com/offer/533795553417.html?sitename=accessory&sku=SP_800291',
                            'https://detail.1688.com/offer/536887968881.html?sitename=accessory&sku=SP_800292',
                            'https://detail.1688.com/offer/44735153913.html?sitename=accessory&sku=SP_800293',
                            'https://detail.1688.com/offer/45435124742.html?sitename=accessory&sku=SP_800294',
                            'https://detail.1688.com/offer/38993500760.html?sitename=accessory&sku=SP_800295',
                            'https://detail.1688.com/offer/533006894668.html?sitename=accessory&sku=SP_800296',
                            'https://detail.1688.com/offer/44229757360.html?sitename=accessory&sku=SP_800297',
                            'https://detail.1688.com/offer/522062926228.html?sitename=accessory&sku=SP_800298',
                            'https://detail.1688.com/offer/36415556252.html?sitename=accessory&sku=SP_800299',
                            'https://detail.1688.com/offer/525846250882.html?sitename=accessory&sku=SP_800300',
                            'https://detail.1688.com/offer/525848594518.html?sitename=accessory&sku=SP_800301',
                            'https://detail.1688.com/offer/525871361590.html?sitename=accessory&sku=SP_800302',
                        ]
            feeder.init_test_feeds(start_urls)
        else:
            feeder.init_feeds(spider_name=spider.name,
                feed_type=spider.feed_type)

        # for collection and products relationship
        for feed in feeder.collection_feeds:
            collection = feed[0].strip()
            url = spider.convert_url(feed[2].strip())
            spider.start_urls.append(url)
            collection_set = feeder.collections(url)
            collection_set.add(collection)
            feeder.map_url_collections(url, collection_set)

    def close_spider(self, spider):
        return  # TODO: currently, we don't update crawl time
        if spider.settings['VERSION'] == 'RELEASE':
            feeder = spider.feeder
            feeder.update_next_crawl_datetime()

    def __assert_necessary_attributes(self, item):
        assert_fields = ('title', 'price', 'collections', 'image_urls', 'sku')
        for field in assert_fields:
            if item.get(field) is None:
                raise DropItem("Missing field [%s] in %s" % (field, item))
        if len(item.get('images')) == 0:
            raise DropItem("Download images error.")
    
    def init_to_excel(self , item):
        dir = os.path.dirname(os.path.realpath(__file__))
        wb = load_workbook(os.path.join(dir,'..','..','terms-products.xlsx'))
        ws = wb.active
        data = []
        data.append(item['referer'])
        data.append(item['url'])
        data.append(item['product_id'])
        ws.append(data)
        wb.save(os.path.join(dir,'terms-products.xlsx'))

    def store(self ,item):
        dir = os.path.dirname(os.path.realpath(__file__))
        wb = load_workbook(os.path.join(dir,'..','..','products.xlsx'))
        ws = wb.active
        data = []
        data.append(item['url'])
        data.append(item['sku'])        
        data.append(json.dumps(item['features'], ensure_ascii=False))
        ws.append(data)
        print 'write to excel ok'
        wb.save(os.path.join(dir,'products.xlsx'))
        
    
    def store_to_excel(self , item):
        dir = os.path.dirname(os.path.realpath(__file__))
        wb = load_workbook(os.path.join(dir,'..','..','products.xlsx'))
        ws = wb.active
        data = []
        data.append(item['sku'])
        data.append(item['product_id'])
        data.append('dress')
        data.append(item['title'])
        data.append(item['description'])
        data.append(item['price'][len('USD '):])
        data.append(item['list_price'][len('USD '):])
        data.append('1.5')
        data.append('2')
        data.append('Blushing Pink%%Champagne%%Iovry%%White')
        data.append('')
        data.append('')
        data.append('2%%4%%6%%8%%10%%12%%14%%16%%16W%%18W%%20W%%22W%%24W%%26W')
        
        data.append(item['features']['SILHOUETTE'].replace(', ','%%') if 'SILHOUETTE' in item['features'] else '')
        data.append(item['features']['HEMLINE / TRAIN'].replace(', ','%%') if 'HEMLINE / TRAIN' in item['features'] else '')
        data.append(item['features']['NECKLINE'].replace(', ','%%') if 'NECKLINE' in item['features'] else '')
        data.append(item['features']['SLEEVE LENGTH'].replace(', ','%%') if 'SLEEVE LENGTH' in item['features'] else '')
        data.append(item['features']['WAIST'].replace(', ','%%') if 'WAIST' in item['features'] else '')
        data.append(item['features']['SLEEVE'].replace(', ','%%') if 'Sleeve' in item['features'] else '')
        data.append(item['features']['FABRIC'].replace(', ','%%') if 'FABRIC' in item['features'] else '')
        data.append(item['features']['EMBELLISHMENT'].replace(', ','%%') if 'EMBELLISHMENT' in item['features'] else '')
        data.append('Yes')
        data.append('Yes')
        data.append(item['features']['BONING'].replace(', ','%%') if 'Boning' in item['features'] else '')
        data.append('')
        data.append(item['features']['BODY SHAPE'].replace(', ','%%') if 'BODY SHAPE' in item['features'] else '')
        data.append(item['features']['BELT FABRIC'].replace(', ','%%') if 'Belt Fabric' in item['features'] else '')
        data.append(item['features']['BACK STYLE'].replace(', ','%%') if 'Back Style' in item['features'] else '')
        data.append('')
        data.append(item['features']['TREND'].replace(', ','%%') if 'Trend' in item['features'] else '')
        data.append(item['features']['STYLE'].replace(', ','%%')  if 'STYLE' in item['features'] else '')
        data.append(item['features']['OCCASION'].replace(', ','%%') if 'Occasion' in item['features'] else '')
        data.append(item['features']['SEASON'].replace(', ','%%') if 'SEASON' in item['features'] else '')
        data.append(item['features']['WEDDING VENUES'].replace(', ','%%') if 'WEDDING VENUES' in item['features'] else '')
        data.append('5')
        data.append('789')
        
        ws.append(data)
        wb.save(os.path.join(dir,'products.xlsx'))
        
        if len(item['review_list']) != 0:
            wb = load_workbook(os.path.join(dir,'reviews.xlsx'))
            ws = wb.active
            for rev in item['review_list']:
                reviews = []
                reviews.append(item['sku'])
                reviews.append(rev['name'])
                reviews.append(rev['content'])
                
                ws.append(reviews)
                wb.save(os.path.join(dir,'reviews.xlsx'))

class AvarshaS3FilesStore(S3FilesStore):
    def __init__(self, *args, **kwargs):
        super(AvarshaS3FilesStore, self).__init__(*args, **kwargs)

    def stat_file(self, path, info):
        def _onsuccess(boto_key):
            checksum = boto_key.etag.strip('"')
            last_modified = boto_key.last_modified
            modified_tuple = rfc822.parsedate_tz(last_modified)
            modified_stamp = int(rfc822.mktime_tz(modified_tuple))
            return {'checksum': checksum,
                    'last_modified': modified_stamp,
                    'width': boto_key.metadata.width,
                    'height': boto_key.metadata.height}
        return self._get_boto_key(path).addCallback(_onsuccess)

class AvarshaImagePipeline(ImagesPipeline):
    def __init__(self, *args, **kwargs):
        self.STORE_SCHEMES['s3'] = AvarshaS3FilesStore
        super(ImagesPipeline, self).__init__(*args, **kwargs)

    def media_to_download(self, request, info):
        def _onsuccess(result):
            if not result:
                return  # returning None force download

            last_modified = result.get('last_modified', None)
            if not last_modified:
                return  # returning None force download

            age_seconds = time.time() - last_modified
            age_days = age_seconds / 60 / 60 / 24
            if age_days > self.EXPIRES:
                return  # returning None force download

            referer = request.headers.get('Referer')
            log.msg(format='File (uptodate): Downloaded %(medianame)s from %(request)s referred in <%(referer)s>',
                    level=log.DEBUG, spider=info.spider,
                    medianame=self.MEDIA_NAME, request=request, referer=referer)
            self.inc_stats(info.spider, 'uptodate')

            checksum = result.get('checksum', None)
            width = result.get('width', None)
            height = result.get('height', None)
            return {'url': request.url, 'path': path, 'checksum': checksum, 'width': width, 'height': height}

        path = self.file_path(request, info=info)
        dfd = defer.maybeDeferred(self.store.stat_file, path, info)
        dfd.addCallbacks(_onsuccess, lambda _: None)
        dfd.addErrback(log.err, self.__class__.__name__ + '.store.stat_file')
        return dfd


    def media_downloaded(self, response, request, info):
        # extend width and height to item['images']
        default_meta = super(ImagesPipeline, self).\
            media_downloaded(response, request, info)
        (width, height) = self.get_image_sizes(response, request)
        return dict(default_meta.items()
            + {'width': width, 'height': height}.items())

    def get_image_sizes(self, response, request):
        orig_image = Image.open(StringIO(response.body))
        width, height = orig_image.size
        return (width, height)

    def file_path(self, request, response=None, info=None):
        ## start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('ImagesPipeline.image_key(url) and file_key(url) methods are deprecated, '
                          'please use file_path(request, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from image_key or file_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        # detect if file_key() or image_key() methods have been overridden
        if not hasattr(self.file_key, '_base'):
            _warn()
            return self.file_key(url)
        elif not hasattr(self.image_key, '_base'):
            _warn()
            return self.image_key(url)
        ## end of deprecation warning block
        
        index = url[url.find('?index=') + len('?index='):url.find('&sku=')]
        sku = url[url.find('&sku=') + len('&sku='):url.find('&dir=')]
        dir = url[url.find('&dir=') + len('&dir='):]
        
        return '1688/%s/%s_(%s).jpg' % (dir,sku,index)