# -*- coding: utf-8 -*-
# author: yangxiao

import re

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'harrods'

class HarrodsSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["harrods.com"]

    def __init__(self, *args, **kwargs):
        super(HarrodsSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        if 'search' in sel.response.url:
            base_url = ''
        else:
            base_url = 'http://www.harrods.com'
        items_xpath = ('//ul[@class="products_row clearfix top "]/li/h3/a/@href'
            '| //ul[@class="products_row "]/li/h3/a/@href'
            '| //ul[@class="products_row top"]/li/h3/a/@href'
            '| //ul[@class="products_row"]/li/h3/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        if 'search' in sel.response.url:
            base_url = ''
        else:
            base_url = 'http://www.harrods.com'
        nexts_xpath = ('//div[@class="pages"]/ul/li[position()<last()]/a/@href|'
            '//a[@class="pageselectorlink"]/@href')

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@class="productname"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'harrods'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//span[@itemprop="brand"]'
            '/span[@class="brand"]/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@class="product_code"]/@data-prodid'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//dl[@id="overview"]/* |'
            '//dl[@id="details"]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//ul[@class="alt_view"]/li/a/@href |'
            '//a[@id="product_img"]/@href')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = list(set(data))

    def _extract_colors(self, sel, item):
        colors_xpath = ('//select[@id="colour"]/option/text()')
        data = sel.xpath(colors_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        sizes_xpath = '//select[@id="size"]/option/text()'
        data = sel.xpath(sizes_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_prices(self, sel, item):
        price_xpath = ('//span[@class="prices price"]'
            '/span[@class="now"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            try:
                price_number = re.search('\xa3(.+)', data[0]).group(1)
                item['price'] = self._format_price("GBP ", price_number)
            except:
                self.log('Fail to extract price.', log.DEBUG)
            list_price_xpath = ('//span[@class="prices price"]'
                '/span[@class="was"]/text()')
            data = sel.xpath(list_price_xpath).extract()
            if len(data) != 0:
                try:
                    price_number = re.search('\xa3(.+)', data[0]).group(1)
                    item['list_price'] = \
                        self._format_price("GBP ", price_number)
                except:
                    self.log('Fail to extract list price.', log.DEBUG)
        else:
            price_xpath = ('//span[@itemprop="price"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                try:
                    price_number = re.search('\xa3(.+)', data[0]).group(1)
                    item['price'] = self._format_price("GBP ", price_number)
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
