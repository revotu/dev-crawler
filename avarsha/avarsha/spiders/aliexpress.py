# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline
import urllib2
import re
import json

from w3lib.html import remove_tags
from avarsha_spider import AvarshaSpider
from scrapy.selector import Selector
from openpyxl import load_workbook

_spider_name = 'aliexpress'

class AliexpressSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["aliexpress.com"]

    def __init__(self, *args, **kwargs):
        super(AliexpressSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        
        base_url = ''
        items_xpath = ''

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = ''

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="product-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        pass

    def _extract_sku(self, sel, item):
        item['sku'] = sel.response.url[sel.response.url.rfind('/') + len('/'): sel.response.url.find('.htm')]

    def _extract_features(self, sel, item):
        features_key_xpath = '//ul[@class="product-property-list util-clearfix"]/li/span[@class="propery-title"]/text()'
        features_value_xpath = '//ul[@class="product-property-list util-clearfix"]/li/span[@class="propery-des"]/text()'
        data_key = sel.xpath(features_key_xpath).extract()
        data_value = sel.xpath(features_value_xpath).extract()
        if len(data_key) > 0 and len(data_value) > 0:
            item['features'] = dict(zip(data_key,data_value))

    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        category_xpath = '//div[@class="container"]/a/text() | //div[@class="container"]/h2/a/text()'
        data = sel.xpath(category_xpath).extract()
        if len(data) > 0:
            item['size_chart'] = ' > '.join(data)

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        dir = 'aliexpress'
        
        imgs_xpath = '//ul[@id="j-image-thumb-list"]/li/span/img/@src | //div[@id="magnifier"]//img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            data = [img[:img.find('.jpg') + len('.jpg')] for img in data]
            data = list(set(data))
            item['image_urls'] = [ img + '?index=' + str(index + 1) + '&sku=' + item['sku'] + '&dir=' + dir for index ,img in enumerate(list(set(data)))]

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@id="j-sku-price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = data[0].strip()

    def _extract_list_price(self, sel, item):
        pass

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        pass

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
