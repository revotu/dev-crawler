# -*- coding: utf-8 -*-
# author: yangxiao


import re

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'barneys'

class BarneysSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["barneys.com"]

    def __init__(self, *args, **kwargs):
        super(BarneysSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        if '#' in url:
            return url[:url.index('#')]
        if ' ' in url:
            return url.replace(' ', '%20')
        else:
            return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = ('//a[@class="thumb-link"]/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = ('//li[@class="page-no"]/a/@href')

        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_urls.append(self.convert_url(list_url))
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@id="product-content"]'
            '/h1[@class="product-name"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'barneys'

    def _extract_brand_name(self, sel, item):
        brand_xpath = ('//div[@id="product-content"]'
            '/h1[@class="brand"]/a/text()')
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        item['sku'] = re.search('Style &#35; (.+)', sel.response.body).group(1)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@id="collapseOne"]'
            '/div[@class="panel-body standard-p"]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//div[@id="product-image-carousel"]'
            '//figure/a/@data-zoom |'
            '//figure[@class="product-primary-image"]/img/@src')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        item['colors'] = \
            list(set(re.findall('color:"(.+?)"', sel.response.body)))

    def _extract_sizes(self, sel, item):
        size_xpath = ('//ul[@class="swatches size"]'
            '/li[@class="emptyswatch"]/a/text()')
        size_list = sel.xpath(size_xpath).extract()
        if len(size_list) != 0:
            item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="product-price"]'
            '/span[@class="price-sales"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            if data[0] == 'N/A':
                self.log('This product is out of stock.', log.DEBUG)
            price_number = data[0].replace('$', '')
            item['price'] = self._format_price("USD ", price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="product-price"]'
            '/span[@class="price-standard"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].replace('$', '')
            item['list_price'] = self._format_price("USD ", price_number)

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
