# -*- coding: utf-8 -*-
# author: zhujun

import time
import urllib
from sets import Set

from scrapy import log
from scrapy.utils.project import get_project_settings

from avarsha.dynamo_db import DynamoDB


class Feeds(object):
    def __init__(self):
        self.url_collections = {}  # list_url:collections
        self.collection_feeds = []

        self.settings = get_project_settings()
        self.dynamo_db = DynamoDB()

    def init_test_feeds(self, start_urls):
        """For test spider"""
        sequence_number = 0
        for start_url in start_urls:
            start_url = self.__url_quote(start_url)
            self.collection_feeds.append(
                ('test collection ' + str(sequence_number),
                 sequence_number, start_url, 7))
            sequence_number += 1

    def init_feeds(self, spider_name, feed_type):
        now = int(time.time())

        items = self.dynamo_db.table('collection_feeds').query_2(
            index='spider_name_index',
            spider_name__eq=spider_name,
            next_crawl_datetime__lte=now,
            query_filter={'feed_type__eq':feed_type})

        for item in items:
            # collection feeds are divided into different spider hosts
            hash_id = abs(hash(item['collection']))
            if (hash_id % self.settings['NUMBER_OF_HOSTS']
                != self.settings['CRAWLER_NO']):
                continue

            self.collection_feeds.append((
                item['collection'],
                item['sequence_number'],
                self.__url_quote(item['url']),
                item['crawl_period']))
            log.msg('fetch_feed: %s[%d], %s'
                % (item['collection'], item['sequence_number'], item['url']),
                log.DEBUG)

    def update_next_crawl_datetime(self):
        """decide which feeds will be crawled next time"""
        SECONDS_PER_DAY = 86400
        now = int(time.time())
        for feed in self.collection_feeds:
            collection = feed[0]
            sequence_number = feed[1]
            crawl_period = feed[3]
            next_crawl_datetime = now + crawl_period * SECONDS_PER_DAY
            item = self.dynamo_db.table('collection_feeds').get_item(
                collection=collection,
                sequence_number=sequence_number)
            item['next_crawl_datetime'] = next_crawl_datetime
            item.save()
            log.msg('update_next_crawl_datetime: %s[%d]'
                % (collection, sequence_number), log.DEBUG)

    def map_url_collections(self, url, collection_set):
        self.url_collections[url] = collection_set

    def collections(self, url):
        collection_set = Set(self.url_collections.get(url))
        return collection_set

    def __url_quote(self, url):
        # urls like this may fail:
        # http://www.saksoff5th.com/appliqué-fit-and-flare-dress/0494638975296.html
        try:
            url = url.encode('utf-8')
            return urllib.quote(urllib.unquote(url), safe=",/?:@&=+$#")
        except:
            log.msg(('url quote error. %s' % url), log.DEBUG)
            return url


def main():
    spiders = ["6pm", "adasa"]

    feed = Feeds()
    for spider in spiders:
        feed.init_feeds(spider_name=spider, feed_type='PRODUCT')
        print spider, '\t', len(feed.collection_feeds)
        feed.collection_feeds = []
    # feed.update_next_crawl_datetime(data)

if  __name__ == '__main__':
    main()
