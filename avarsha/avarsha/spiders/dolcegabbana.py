# -*- coding: utf-8 -*-
# author: yangxiao

import re

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'dolcegabbana'

class DolcegabbanaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["dolcegabbana.com"]

    def __init__(self, *args, **kwargs):
        super(DolcegabbanaSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://store.dolcegabbana.com'
        items_xpath = ('//a[@data-itemlink=""]/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = ('//a[@class="navNextButton"]/@href')

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@id="itemTechSheet"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'dolcegabbana'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Dolce&Gabbana'

    def _extract_sku(self, sel, item):
        sku_xpath = '//meta[@type="SKU"]/@content'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="scrollCnt"]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//div[@id="imageList"]/img/@src')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = map(lambda i: i.replace('11', '14'), data)

    def _extract_colors(self, sel, item):
        colors_xpath = ('//ul[@id="colorsContainer"]/li/@data-title')
        data = sel.xpath(colors_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        sizes_xpath = '//ul[@id="sizesContainer"]/li/@data-title'
        data = sel.xpath(sizes_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_prices(self, sel, item):
        price_xpath = ('//div[@class="newprice"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            try:
                price_number = data[0][2:]
                item['price'] = self._format_price("USD ", price_number)
            except:
                self.log('Fail to extract price.', log.DEBUG)
            list_price_xpath = ('//div[@class="oldprice"]/text()')
            data = sel.xpath(list_price_xpath).extract()
            if len(data) != 0:
                try:
                    price_number = data[0][2:]
                    item['list_price'] = \
                        self._format_price("USD ", price_number)
                except:
                    self.log('Fail to extract list price.', log.DEBUG)
        else:
            price_xpath = ('//div[@class="price"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                try:
                    price_number = data[0][2:]
                    item['price'] = self._format_price("USD ", price_number)
                except:
                    self.log('Fail to extract price.', log.DEBUG)

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
