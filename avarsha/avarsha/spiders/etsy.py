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

_spider_name = 'etsy'

class EtsySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["etsy.com"]
    brand_list = []

    def __init__(self, *args, **kwargs):
        super(EtsySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        
        base_url = ''
        items_xpath = '//div[@class="block-grid-item listing-card position-relative parent-hover-show"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="pagination btn-group clearfix mt-xs-3"]/a[last()]/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        return
        title_xpath = '//span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        return
        item['store_name'] = 'Etsy'

    def _extract_brand_name(self, sel, item):
        brand_reg = re.compile(r'"shop_name":"(.+?)"')
        data = brand_reg.findall(sel.response.body)
        if len(data) != 0:
            item['brand_name'] = data[0].strip()
            self.brand_list.append(item['brand_name'])
            self.brand_list = list(set(self.brand_list))
            print self.brand_list
            fd = open('brand', "w")
            for brand in self.brand_list:
                fd.write("%s\n" % brand)
            fd.close()

    def _extract_sku(self, sel, item):
        item['sku'] = sel.response.url[sel.response.url.find('listing/') + len('listing/'): sel.response.url.rfind('/')]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        return
        desc_xpath = '//div[@id="item-overview"]/ul/li/node()'
        data = sel.xpath(desc_xpath).extract()
        if len(data) != 0:
            data = [remove_tags(v.strip()) for v in data]
            description = ';'.join(data).replace(':;',':').replace('from;','from ')
            item['description'] = description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        return
        dir = sel.response.url[sel.response.url.find('ref=') + len('ref='):]
        imgs_xpath = '//ul[@id="image-carousel"]/li/@data-full-image-href'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = [ img + '?index=' + str(index + 1) + '&sku=' + item['sku'] + '&dir=' + dir for index ,img in enumerate(list(set(data)))]

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        return
        price_xpath = '//meta[@property="etsymarketplace:price_value"]/@content'
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
        #review need nickname and content
        pass

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
