# -*- coding: utf-8 -*-
# author: huoda

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'tibi'

class TibiSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["tibi.com"]

    def __init__(self, *args, **kwargs):
        super(TibiSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.tibi.com'
        items_xpath = '//*[@class="product-name"]/a//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.tibi.com'
        nexts_xpath = '//*[@title="Next"][1]//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="product-main-info"]/div'
            '[@class="product-name"]/h1/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'tibi'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'tibi'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="product-sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="desc-content"]/div[@class="std"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        img_xpath = '//*[@id="ul-moreviews"]//a//@href'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//div[@class="swatchesContainer"]//img//@title'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = ('//dd[@class="last"]//span'
            '[@class="swatch swatch-empty"]/text()')
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@class="regular-price"]/'
            'span[@class="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            data[0] = data[0].strip()
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = ('//*[@class="special-price"]/'
                'span[@class="price"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                data[0] = data[0].strip()
                price_number = data[0][len('$'):].strip()
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@class="old-price"]/span[@class="price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data[0] = data[0].strip()
            list_price_number = data[0][len('$'):].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
