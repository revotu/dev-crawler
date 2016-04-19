# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = '1stdibs'

class FirstdibsSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["1stdibs.com"]

    def __init__(self, *args, **kwargs):
        super(FirstdibsSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.1stdibs.com'
        items_xpath = '//div[@class="product-name"]/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'https://www.1stdibs.com'
        nexts_xpath = (
            '//li[@class="pagination-item is-arrow is-right is-last"]/a/@href')

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="item-title"]/span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = "1stdibs"

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//td[@data-tn="pdp-spec-brand"]/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()
        else:
            item['brand_name'] = "1stdibs"

    def _extract_sku(self, sel, item):
        sku_xpath = '//td[@data-tn="pdp-spec-reference-number"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        features_xpath = '//div[@class="item-data"]//tr'
        data = sel.xpath(features_xpath).extract()
        _features = {}
        _key = ''
        _value = ''
        if len(data) != 0:
            for line in data:
                idx1 = line.find('<td>')
                if(idx1 != -1):
                    idx2 = line.find('</td>', idx1)
                    _key = line[idx1 + len('<td>'):idx2].replace(':', '').strip()
                    line = line[idx2:]
                idx1 = line.find('<td>')
                if(idx1 != -1):
                    idx2 = line.find('</td>', idx1)
                    _value = line[idx1 + len('<td>'):idx2]
                    data_re = re.compile(r'(?:<[^<>]*>)|\n+|\t+|\r+')
                    _value = data_re.sub('', _value).strip()
                if(len(_key) != 0 and len(_value) != 0):
                    _features[_key] = _value
            item['features'] = _features

    def _extract_description(self, sel, item):
        description_xpath = '//p[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        image_url = ''
        imgs_url_xpath = '//ul[@class="carousel-items swiper-wrapper"]//img/@src'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        if(len(data_imgs) != 0):
            for line in data_imgs:
                if(line.find('https:') == -1):
                    image_url = ''.join(['https:', line])
                imgs.append(image_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        currency_xpath = '//meta[@property="product:price:currency"]/@content'
        amount_xpath = '//meta[@property="product:price:amount"]/@content'
        currency = sel.xpath(currency_xpath).extract()
        amount = sel.xpath(amount_xpath).extract()
        if(len(amount) != 0):
            _price = amount[0]
            if(len(currency) != 0):
                _currency = currency[0]
                item['price'] = self._format_price(_currency, _price)

    def _extract_list_price(self, sel, item):
        pass

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
