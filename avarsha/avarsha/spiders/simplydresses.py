# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re

from avarsha_spider import AvarshaSpider


_spider_name = 'simplydresses'

class SimplydressesSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["simplydresses.com"]
    sku = 328681

    def __init__(self, *args, **kwargs):
        super(SimplydressesSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.simplydresses.com'
        items_xpath = '//div[@class="product-body"]//a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        requests = []
        list_urls = ['http://www.simplydresses.com/plus-size-prom-dresses/plusview_all?key=plusview_all&size=&color=&price=&nt=32&sr=33&ob=da&',
                     'http://www.simplydresses.com/plus-size-prom-dresses/plusview_all?key=plusview_all&size=&color=&price=&nt=32&sr=65&ob=da&',
                     'http://www.simplydresses.com/plus-size-prom-dresses/plusview_all?key=plusview_all&size=&color=&price=&nt=32&sr=97&ob=da&',
                     'http://www.simplydresses.com/plus-size-prom-dresses/plusview_all?key=plusview_all&size=&color=&price=&nt=32&sr=129&ob=da&',
                     'http://www.simplydresses.com/plus-size-prom-dresses/plusview_all?key=plusview_all&size=&color=&price=&nt=32&sr=161&ob=da&',
                     'http://www.simplydresses.com/plus-size-prom-dresses/plusview_all?key=plusview_all&size=&color=&price=&nt=32&sr=193&ob=da&',
                    ]
        for list_url in list_urls:
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h2[@class="single-product-title"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) > 0:
            item['title'] = data[0].strip()

    def _extract_sku(self, sel, item):
        item['sku'] = self.sku

    def _extract_image_urls(self, sel, item):
        imgs = []
        img_xpath = '//div[@class="single-product-slider"]//div[@class="slide-image slide-real-image"]/@data-zoom-src'
        data = sel.xpath(img_xpath).extract()
        if len(data) > 0:
            index = 1
            for img in data:
                imgs.append('http:' + img + '?sku=' + str(self.sku) + '&index=' + str(index))
                index += 1
        self.sku += 1
        item['image_urls'] = imgs
    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="single-product-main"]//strong/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) > 0:
            item['price'] = self._format_price('USD', data[0][len('$'):])


def main():
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()