'''
Created on 2015/6/18

@author: zhujun
'''

import time
import traceback

import boto.dynamodb2
from boto.dynamodb2.table import Table
from scrapy.utils.project import get_project_settings

class DynamoDB(object):
    def __init__(self):
        settings = get_project_settings()
        self.conn = boto.dynamodb2.connect_to_region(
            'us-west-1',
            aws_access_key_id=settings['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=settings['AWS_SECRET_ACCESS_KEY'])

        self.products_table = None
        self.product_shopstyle_likes_table = None
        self.product_polyvore_likes_table = None
        self.product_facebook_stats_table = None
        self.chrome_table = None

#         self.products_table = Table(
#             'products',
#             connection=self.conn)
#
#         self.product_availabity_table = Table(
#             'product_availabity',
#             connection=self.conn)
#
#         self.product_sales_table = Table(
#             'product_sales',
#             connection=self.conn)
#
#         self.product_reviews_table = Table(
#             'product_reviews',
#             connection=self.conn)


    def get_product_id_by_url(self, url):
        if self.products_table is None:
            self.products_table = Table('products', connection=self.conn)

        items = self.products_table.query_2(index='url-index', url__eq=url)
        for item in items:
            return item['product_id']

    def fetch_product_urls(self, segment, total_segments):
        if self.products_table is None:
            self.products_table = Table('products', connection=self.conn)

        results = self.products_table.scan(segment=segment, total_segments=total_segments)
        return results

    def save_shopstyle_likes(self, product_id, like_count, crawl_datetime):
        if self.product_shopstyle_likes_table is None:
            self.product_shopstyle_likes_table = Table(
                'product_shopstyle_likes',
                connection=self.conn)

        item = {}
        item['product_id'] = product_id
        item['shopstyle_likes'] = like_count
        item['crawl_datetime'] = int(crawl_datetime)
        try:
            self.product_shopstyle_likes_table.put_item(data=item, overwrite=True)
        except:
            print traceback.print_exc()

    def save_polyvore_likes(self, product_id, like_count, crawl_datetime):
        if self.product_polyvore_likes_table is None:
            self.product_polyvore_likes_table = Table(
                'product_polyvore_likes',
                connection=self.conn)

        item = {}
        item['product_id'] = product_id
        item['polyvore_likes'] = like_count
        item['crawl_datetime'] = int(crawl_datetime)
        try:
            self.product_polyvore_likes_table.put_item(data=item, overwrite=True)
        except:
            print traceback.print_exc()

    def save_facebook_stats(self, product_id, share_count, like_count, comment_count):
        if self.product_facebook_stats_table is None:
            self.product_facebook_stats_table = Table(
                'product_facebook_stats',
                connection=self.conn)

        item = {}
        item['product_id'] = product_id
        item['share_count'] = share_count
        item['like_count'] = like_count
        item['comment_count'] = comment_count
        item['crawl_datetime'] = int(time.time())
        try:
            self.product_facebook_stats_table.put_item(data=item, overwrite=True)
        except:
            print traceback.print_exc()

    def save_chrome_log(self, url, clicks, datetime):
        if self.chrome_table is None:
            self.chrome_table = Table('chrome', connection=self.conn)
        item = {'url':url, 'clicks':clicks, 'datetime':datetime}
        try:
            self.chrome_table.put_item(data=item, overwrite=True)
        except:
            print traceback.print_exc()

    def get_chrome_clicks(self, url, datetime=None):
        if self.chrome_table is None:
            self.chrome_table = Table('chrome', connection=self.conn)
        try:
            item = self.chrome_table.get_item(url=url)
            return item['clicks']
        except:
            return -1
