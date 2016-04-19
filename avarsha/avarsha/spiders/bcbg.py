# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'bcbg'

class BcbgmaxazriaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["bcbg.com"]

    def __init__(self, *args, **kwargs):
        super(BcbgmaxazriaSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = ('//ul[@id="search-result-items"]//'
            'li//div[@class="product-name"]//a/@href')

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//a[@class="page-next"]/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="pdp-detailinfo"]'
            '/div/h1[@class="product-name"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Bcbgmaxazria'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Bcbgmaxazria'

    def _extract_sku(self, sel, item):
        sku_xpath = ('//div[@class="product-number"]/'
            'span[@itemprop="productID"]/text()')
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'<[^<>]+>|\n+|\r+|\t+|  +')
            _data = data_re.sub('', data[0])
            item['sku'] = str(_data)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description1_xpath = '//div[@itemprop="description"]/p'
        data1 = sel.xpath(description1_xpath).extract()
        description2_xpath = '//div[@itemprop="description"]/ul'
        data2 = sel.xpath(description2_xpath).extract()
        _description = ''
        if len(data1) != 0:
            _description = data1[0]
        if len(data2) != 0:
            _description = ''.join([_description, data2[0]])
        item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_url_xpath = '//div[@class="thumb"]/a/@href'
        imgs_url2_xpath = '//a[@class="product-image main-image"]/@href'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        data2_imgs = sel.xpath(imgs_url2_xpath).extract()
        if len(data_imgs) != 0:
            item['image_urls'] = data_imgs
        elif len(data2_imgs) != 0:
            item['image_urls'] = data2_imgs

    def _extract_colors(self, sel, item):
        color_xpath = ('//div[@class="val_div"]'
            '//div[@class="attribute swatches-color"]'
            '//span[@class="selected-value"]/text()')
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]')
            data[0] = data_re.sub('', data[0])
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size = []
        size_xpath = ('//div[@class="val_div"]//select[@id="va-size"]'
            '//option[not(@disabled)]/text()')
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            for _data in data:
                data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
                _data = data_re.sub('', _data)
                size.append(_data)
            item['sizes'] = sorted(size)

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@id="product-content"]'
            '/div[@class="product-price"]/span[@class="price-sales"]')
        price2_xpath = ('//div[@id="product-content"]/div[@class='
            '"product-price"]/span[@class="original-price"]/text()')
        data = sel.xpath(price_xpath).extract()
        data2 = sel.xpath(price2_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'<[^<>]+>|\n+|\r+|\t+| +|[$]|NOW:')
            price = data_re.sub('', data[0])
            item['price'] = self._format_price('USD', price)
        elif len(data2) != 0:
            data_re = re.compile(r'<[^<>]+>|\n+|\r+|\t+| +|[$]')
            price = data_re.sub('', data2[0])
            item['price'] = self._format_price('USD', price)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@id="product-content"]/div[@class='
            '"product-price"]/span[@class="price-standard"]')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'<[^<>]+>|\n+|\r+|\t+| +|[$]|ORIGINAL:')
            list_price = data_re.sub('', data[0])
            item['list_price'] = self._format_price('USD', list_price)

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

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
