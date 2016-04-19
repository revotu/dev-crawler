# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'billabong'

class BillabongSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["billabong.com"]

    def __init__(self, *args, **kwargs):
        super(BillabongSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        return url.replace('#!', '?')

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = sel.response.url.split('/')
        base_url = '/'.join([base_url[0], base_url[1], base_url[2]])
        items_xpath = '//a[@class="product-text"]/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="product-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Billabong'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Billabong'

    def _extract_sku(self, sel, item):
        sku_xpath = '//h5[@itemprop="sku"]/text()'
        _sku = sel.xpath(sku_xpath).extract()
        if(len(_sku) != 0):
            data_re = re.compile(r'[:]|STYLE')
            item['sku'] = data_re.sub('', _sku[0]).strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description1_xpath = '//div[@class="product-description"]'
        data1 = sel.xpath(description1_xpath).extract()
        description2_xpath = '//div[@class="product-specs"]'
        data2 = sel.xpath(description2_xpath).extract()
        description3_xpath = '//div[@class="product-materials"]'
        data3 = sel.xpath(description3_xpath).extract()
        _description = ''
        if len(data1) != 0:
            _description = ''.join([_description, data1[0]])
        if len(data2) != 0:
            _description = ''.join([_description, data2[0]])
        if len(data3) != 0:
            _description = ''.join([_description, data3[0]])
        item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        base_url = sel.response.url.split('/')
        base_url = '/'.join([base_url[0], base_url[1], base_url[2]])
        imgs_url_xpath = '//div[@class="span12"]//li//a/@data-zoom'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        if len(data_imgs) != 0:
            for image_url in data_imgs:
                image_url = ''.join([base_url, image_url])
                imgs.append(image_url)
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="detail-wrapper"]//'
            'span[@itemprop="price lowPrice"]/text()')
        price = sel.xpath(price_xpath).extract()
        if(len(price) != 0):
            data_re = re.compile(r'(?:<[^<>]>)+|[$]')
            item['price'] = self._format_price(
                'USD', data_re.sub('', price[0]).strip())

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="detail-wrapper"]//'
            'span[@class="regular-price product-regular-price on-sale"]/text()')
        list_price = sel.xpath(list_price_xpath).extract()
        if(len(list_price) != 0):
            data_re = re.compile(r'(?:<[^<>]>)+|[$]')
            item['list_price'] = self._format_price(
                'USD', data_re.sub('', list_price[0]).strip())

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
