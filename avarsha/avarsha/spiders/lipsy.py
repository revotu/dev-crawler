# -*- coding: utf-8 -*-
# author: yangxiao


import re

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'lipsy'

class LipsySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["lipsy.co.uk"]

    def __init__(self, *args, **kwargs):
        super(LipsySpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        if '#' in url:
            return url[:url.index('#')]
        else:
            return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = ('//div[@class="product"]/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        try:
            next_page = re.search('paging-anchor paging-anchor-number '
                'paging-anchor-last-page.*href="(.+?)"',sel.response.body)\
                .group(1)
        except:
            self.log('It is already the last page.', log.DEBUG)
        requests = []
        list_urls.append(self.convert_url(next_page))
        request = scrapy.Request(next_page, callback=self.parse)
        requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@id="titleDesc"]/h1[@itemprop="name"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'lipsy'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'lipsy'

    def _extract_sku(self, sel, item):
        sku_xpath = '//p[@itemprop="sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = re.search('(\S.*\S)', data[0]).group(1)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//p[@class="product-desc"]/text() |'
            '//div[@class="tab-col1"]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//ul[@class="thb-prod-imgs"]/li/a/@href')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//p[@itemprop="color"]/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = \
                map(lambda i:re.search('(\S.*\S)', i).group(1), data)

    def _extract_sizes(self, sel, item):
        size_xpath = ('//button[@class="sizeOption"]/@title')
        size_list = sel.xpath(size_xpath).extract()
        if len(size_list) != 0:
            item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_prices(self, sel, item):
        prices_xpath = '//h2[@class="product-price"]//text()'
        data = sel.xpath(prices_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                data[i] = re.search('\xa3(.+)', data[i]).group(1)
            data.sort()
            if len(data) == 1:
                price_number = data[0]
                item['price'] = self._format_price("GBP ", price_number)
            elif len(data) == 2:
                price_number = data[0]
                item['price'] = self._format_price("GBP ", price_number)
                price_number = data[1]
                item['list_price'] = self._format_price("GBP ", price_number)

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
