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

_spider_name = 'dhgate'

class DhgateSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["dhgate.com"]

    def __init__(self, *args, **kwargs):
        super(DhgateSpider, self).__init__(*args, **kwargs)

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
        title_xpath = '//h1/text()'
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
        features_key_xpath = '//div[@class="item-specifics"]/ul/li/strong/text()'
        features_value_xpath = '//div[@class="item-specifics"]/ul/li/span/b/text()'
        data_key = sel.xpath(features_key_xpath).extract()
        data_value = sel.xpath(features_value_xpath).extract()
        if len(data_key) > 0 and len(data_value) > 0:
            item['features'] = dict(zip(data_key,data_value))

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="description"]/ul/li/node()'
        data = sel.xpath(description_xpath).extract()
        if len(data) > 0:
            data = [remove_tags(v.strip()) for v in data]
            description = ''
            for index,desc in enumerate(data):
                if index % 2 == 0:
                    description += desc
                else :
                    description += desc + ';'
            item['description'] = description

    def _extract_size_chart(self, sel, item):
        #category: 
        category_reg = re.compile(r"content_category: '(.+?)'")
        data = category_reg.findall(sel.response.body)
        if len(data) > 0:
            item['size_chart'] = data[0]

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        dir = 'dhgate'
        img_reg = re.compile(r'b-init="(.+?)"')
        data = img_reg.findall(sel.response.body)

        if len(data) != 0:
            item['image_urls'] = [ img + '?index=' + str(index + 1) + '&sku=' + item['sku'] + '&dir=' + dir for index ,img in enumerate(list(set(data)))]

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        low_price_reg = re.compile(r'"lowPrice": "(.+?)"')
        high_price_reg = re.compile(r'"highPrice": "(.+?)"')
        data_low_price = low_price_reg.findall(sel.response.body)
        data_high_price = high_price_reg.findall(sel.response.body)
        if len(data_low_price) != 0 and len(data_high_price) != 0:
            item['price'] = data_low_price[0].strip() + ' - ' + data_high_price[0].strip()
        elif len(data_low_price) != 0:
            item['price'] = data_low_price[0].strip()
        elif len(data_high_price) != 0:
            item['price'] = data_high_price[0].strip()

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
