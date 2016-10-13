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

_spider_name = 'luulla'

class LuullaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["luulla.com"]

    def __init__(self, *args, **kwargs):
        super(LuullaSpider, self).__init__(*args, **kwargs)

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
        title_xpath = '//title/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip().replace(' on Luulla','')

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        pass

    def _extract_sku(self, sel, item):
        item['sku'] = sel.response.url[sel.response.url.find('product/') + len('product/'): sel.response.url.rfind('/')]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="prd-selection-description-id"]/div[1]/p/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) > 0:
            item['description'] = data

    def _extract_size_chart(self, sel, item):
        #Material Tags
        material_tags_xpath = '//div[@class="float-left border-top-1-dedede width-full padding-bottom-30"]//a[contains(@href,"/material/")]/text()'
        data = sel.xpath(material_tags_xpath).extract()
        if len(data) > 0:
            item['size_chart'] = data

    def _extract_color_chart(self, sel, item):
        #Product Tags
        product_tags_xpath = '//div[@class="float-left border-top-1-dedede width-full padding-bottom-30"]//a[contains(@href,"/tags/")]/text()'
        data = sel.xpath(product_tags_xpath).extract()
        if len(data) > 0:
            item['color_chart'] = data

    def _extract_image_urls(self, sel, item):
        dir = 'luulla'
        img_reg = re.compile(r"'href','(.+?product-original.+?)'")
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
        price_xpath = '//meta[@property="og:price:amount"]/@content'
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
        #Total Followers
        follower_reg = re.compile(r'Total Followers: (\d+)')
        data = follower_reg.findall(sel.response.body)
        if len(data) > 0:
            item['review_count'] = data[0].strip()

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
