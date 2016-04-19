# -*- coding: utf-8 -*-
# author: yangxiao

import re
import HTMLParser
import json

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'tedbaker'

class TedbakerSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["tedbaker.com"]

    def __init__(self, *args, **kwargs):
        super(TedbakerSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.tedbaker.com'
        items_xpath = ('//div[@class="product_list index"]/article/div'
            '/a[@class="image"]/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.tedbaker.com'
        nexts_xpath = ('//li[@class="next"]/a/@href')

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//h1[@class="name"]/text() |'
            '//h2[@class="summary"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'tedbaker'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'tedbaker'

    def _extract_sku(self, sel, item):
        try:
            item['sku'] = re.search('product_code : "(.+?)"', \
                sel.response.body).group(1)
        except:
            self.log('Fail to extract sku.', log.DEBUG)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//p[@class="description"]/text() |'
            '//div[@id="product_details"]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//div[@class="paging_viewport"]//a[@class="image"]'
            '/img/@ng-src')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                data[i] = data[i][:data[i].find('&{')] + \
                    '&w=1024%26h=1280%26q=80'
            item['image_urls'] = list(set(data))

    def _extract_colors(self, sel, item):
        colors_xpath = ('//p[@class="colour_name"]/text()')
        data = sel.xpath(colors_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        sizes_data_xpath = '//*[@id="add_to_cart_form"]//@ng-init'
        data = sel.xpath(sizes_data_xpath).extract()
        if len(data) != 0:
            sizes = []
            data = data[0]
            html_parser = HTMLParser.HTMLParser()
            unescaped = html_parser.unescape(data)
            data = json.loads(unescaped[5:-20])
            data = data['sizeDataList']
            for itemm in data:
                size = itemm['size']
                if itemm['purchasable'] == False:
                    size = size + ' (out of stock)'
                sizes.append(size)
            if len(sizes) != 0:
                item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//header[@id="product_head"]/ul[@class="pricing"]/li[@class="price unit"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            try:
                price_number = re.search('\xa3(.+)', data[0]).group(1)
                item['price'] = self._format_price("GBP ", price_number)
            except:
                self.log('Fail to extract price.', log.DEBUG)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//header[@id="product_head"]/ul[@class="pricing"]/li[@class="price previous"]/del/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            try:
                price_number = re.search('\xa3(.+)', data[0]).group(1)
                item['list_price'] = self._format_price("GBP ", price_number)
            except:
                self.log('Fail to extract list price.', log.DEBUG)

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
