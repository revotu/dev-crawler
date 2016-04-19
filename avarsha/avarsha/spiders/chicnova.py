# -*- coding: utf-8 -*-
# author: yangxiao


import re

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'chicnova'

class ChicnovaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["chicnova.com"]

    def __init__(self, *args, **kwargs):
        super(ChicnovaSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//h2[@class="product-name"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="pages"]/ol/li/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//p[@class="chic_product_name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = re.search('(\w.*\w)', data[0]).group(1)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'chicnova'

    def _extract_brand_name(self, sel, item):
        try:
            item['brand_name'] = \
                re.findall("'brand': '(.*)?'", sel.response.body)[-1]
        except:
            self.log('Fail to get the brand name.', log.DEBUG)

    def _extract_sku(self, sel, item):
        sku_xpath = '//input[@name="sku"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//meta[@name="description"]/@content')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_list_xpath = '//div[@id="zoomWrapper"]/a/@href'
        data = sel.xpath(imgs_list_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = list(set(data))

    def _extract_colors(self, sel, item):
        color_xpath = '//li[@class="swatchContainer"]/img/@title'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//ul[@id="ul-attribute129"]/li/span/text()'
        size_list = sel.xpath(size_xpath).extract()
        if len(size_list) != 0:
            item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_prices(self, sel, item):
        self._extract_list_price(sel, item)
        self._extract_price(sel, item)
        self._extract_low_price(sel, item)
        self._extract_high_price(sel, item)

    def _extract_price(self, sel, item):
        if item.get('list_price') == None:
            price_xpath = ('//div[@class="price-points chic_product_price"]'
                '//span[@class="regular-price"]'
                '/span[@class="price"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0].replace('$', '')
                item['price'] = self._format_price("USD", price_number)
        else:
            price_xpath = ('//div[@class="price-points chic_product_price"]'
                '/div[@class="price-box"]/p[@class="special-price"]'
                '/span[@class="price"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = re.search('(\$.*?)\s', data[-1]).group(1)\
                    .replace('$', '')
                item['price'] = self._format_price("USD", price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="price-points chic_product_price"]'
            '//p[@class="old-price"]/span[@class="price"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = re.search('(\$.*?)\s', data[0]).group(1)\
                .replace('$', '')
            item['list_price'] = self._format_price("USD", price_number)

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
