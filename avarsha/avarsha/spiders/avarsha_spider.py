# -*- coding: utf-8 -*-
# author: zhujun

import abc
import md5
import time
import urllib
from sets import Set

import scrapy
from scrapy import log
from scrapy.selector import Selector

from avarsha.feeds import Feeds
from avarsha.items import ProductItem


class AvarshaSpider(scrapy.Spider):
    def __init__(self, feed_type=None, *args, **kwargs):
        super(AvarshaSpider, self).__init__(*args, **kwargs)

        self.start_urls = []
        self.feeder = Feeds()
        self.url_collections = {}  # list_url:collections

        if feed_type == 'PRODUCT':
            self.feed_type = feed_type
        else:
            self.feed_type = 'LIST'

        # self.feed_type = 'PRODUCT'  # donglongtu  modify for product

    def init_start_urls(self, start_urls):
        for start_url in start_urls:
            self.start_urls.append(self.convert_url(start_url))

    def convert_url(self, url):
        return url

    def parse(self, response):
        # preprocess json response, or xpath does not work
        response = response.replace(body=self._remove_escape(response.body))

        if self.feed_type == 'PRODUCT':
            yield self.parse_item(response)
            return

        self.log('Parse category link: %s' % response.url, log.DEBUG)

        sel = Selector(response)

        item_urls = []
        try:
            for request in self.find_items_from_list_page(sel, item_urls):
                yield request
        except:
            self.log('Exception in find_items_from_list_page', log.ERROR)

        list_urls = []
        try:
            for request in self.find_nexts_from_list_page(sel, list_urls):
                yield request
        except:
            self.log('Exception in find_nexts_from_list_page', log.ERROR)

        # get parent url's collection
        parent_collection_set = self.__collections(response)
        assert parent_collection_set is not None
        for new_url in item_urls + list_urls:
            collection_set = self.feeder.collections(new_url)
            collection_set |= parent_collection_set
            self.feeder.map_url_collections(new_url, collection_set)

    def parse_item(self, response):
        # self.log('Parse item link: %s' % response.url, log.DEBUG)

        sel = Selector(response)
        item = ProductItem()

        # each spider overrides the following methods
        self._extract_url(sel, item)
        self._extract_title(sel, item)
        self._extract_store_name(sel, item)
        self._extract_brand_name(sel, item)
        self._extract_sku(sel, item)
        self._extract_features(sel, item)
        self._extract_description(sel, item)
        self._extract_size_chart(sel, item)
        self._extract_color_chart(sel, item)
        self._extract_image_urls(sel, item)
        self._extract_basic_options(sel, item)
        self._extract_stocks(sel, item)
        self._extract_prices(sel, item)
        self._extract_is_free_shipping(sel, item)
        self._extract_reviews(sel, item)

        # auto filled methods, don't need to override them
        # must include the following methods if you override parse_item
        self._save_product_id(sel, item)
        self._record_crawl_datetime(item)
        self._save_product_collections(sel, item)

        return item

    def _find_items_from_list_page(self, sel, base_url, items_xpath, item_urls):
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _remove_escape(self, content):
        '''Used to preprocess jason data to html data'''
        content = content.replace('\\"', '"')\
            .replace('\\/', '/')\
            .replace('\\n', '')
        return content

    def _format_price(self, currency_unit, price_number):
        # refer to: http://en.wikipedia.org/wiki/List_of_circulating_currencies
        # currency_unit is USD, GBP, CNY, etc.
        return currency_unit.strip() + ' ' + price_number.strip()

    def _generate_product_id(self, item):
        if item.get('sku') is None:
            self.log('Sku not scrapyed.', log.DEBUG)
            return '0000000000000000'
        id_feed_string = self.name + item['sku']

        m = md5.new()
        m.update(id_feed_string)
        return m.hexdigest()[:16]

    def _save_product_id(self, sel, item):
        item['product_id'] = self._generate_product_id(item)

    def _record_crawl_datetime(self, item):
        now = int(time.time())
        item['crawl_datetime'] = now

    def _save_product_collections(self, sel, item):
        collections = self.__collections(sel.response)
        if len(collections) != 0:
            item['collections'] = collections

    def _url_quote(self, url):
        return urllib.quote(url, safe=",/?:@&=+$#")

    def __collections(self, response):
        collection_set = self.feeder.collections(response.url)
        for redirect_url in Set(response.meta.get('redirect_urls')):
            collection_set |= self.feeder.collections(redirect_url)
        return collection_set

    @abc.abstractmethod
    def find_items_from_list_page(self, sel, item_urls):
        pass

    @abc.abstractmethod
    def find_nexts_from_list_page(self, sel, list_urls):
        pass

    # the following methods are used to extract product attributes
    def _extract_url(self, sel, item):
        pass

    def _extract_title(self, sel, item):
        pass

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        pass

    def _extract_sku(self, sel, item):
        pass

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        pass

    def _extract_basic_options(self, sel, item):
        # include _extract_colors and _extract_sizes as default
        # could be extended to other options, eg, length for hair
        self._extract_colors(sel, item)
        self._extract_sizes(sel, item)

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_prices(self, sel, item):
        self._extract_price(sel, item)
        self._extract_list_price(sel, item)
        self._extract_low_price(sel, item)
        self._extract_high_price(sel, item)

    def _extract_price(self, sel, item):
        pass

    def _extract_list_price(self, sel, item):
        pass

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        pass

    def _extract_reviews(self, sel, item):
        self._extract_review_count(sel, item)
        self._extract_review_rating(sel, item)
        self._extract_max_review_rating(sel, item)
        self._extract_review_list(sel, item)

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass
