# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'balmain'

class BalmainSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["balmain.com"]

    def __init__(self, *args, **kwargs):
        super(BalmainSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//a[@class="product-image"]/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="wrap-context"]//div[@class="title"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Balmain'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Balmain'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|Ref:')
            _sku = data_re.sub('', data[0])
            item['sku'] = str(_sku)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="std"]')
        description2_xpath = ('//div[@id="composition_desc"]')
        data = sel.xpath(description_xpath).extract()
        data2 = sel.xpath(description2_xpath).extract()
        _description = ''
        if len(data) != 0:
            _description = data[0]
        if len(data2) != 0:
            _description = _description + data2[0]
        if len(_description) != 0:
            item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        image_urls_xpath = '//img[@class="myimg"]/@src'
        data = sel.xpath(image_urls_xpath).extract()
        if len(data) != 0:
            for line in data:
                if(line.find('http:') == -1):
                    line = 'http:' + line
                imgs.append(line)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@class="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(u'<[^<>]+>|\n+|\r+|\t+|[ €$]|\xa0|,00')
            new_data = data_re.sub('', data[0])
            if(data[0].find(u'€') != -1):
                item['price'] = self._format_price('EUR', new_data)
            elif(data[0].find(u'$') != -1):
                item['price'] = self._format_price('USD', new_data)

    def _extract_list_price(self, sel, item):
        pass

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        item['is_free_shipping'] = True

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
