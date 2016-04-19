# -*- coding: utf-8 -*-
# author: tanyafeng

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'forzieri'

class ForzieriSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["forzieri.com"]

    def __init__(self, *args, **kwargs):
        super(ForzieriSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.forzieri.com'
        items_xpath = '//*[@class="product_list_item_info clear"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        requests = []
        base_url = 'http://www.forzieri.com'
        nexts_xpath = '//*[@class="next-page"]/@href'
        data = sel.xpath(nexts_xpath).extract()
        if len(data) != 0:
            list_url = base_url + data[0]
            list_urls.append(list_url)
            requests.append(scrapy.Request(list_url, callback = self.parse))
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@property="og:title"]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Forzieri'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@itemprop="brand"]/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="product_sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@itemprop="description"]/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ' '.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        image_xpath = '//*[@id="productThumbs"]/a/@href'
        data = sel.xpath(image_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//*[@id="variants"]//ul/li/a/img/@alt'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//*[@id="variants"]'
        size_pattern = re.compile('>(\d*) \(')
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            match = size_pattern.findall(data[0])
            if len(match) != 0:
                item['sizes'] = match

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_str = []
        currency_xpath = '//*[@itemprop="priceCurrency"]/@content'
        data = sel.xpath(currency_xpath).extract()
        if len(data) != 0:
            price_str.append(data[0])
        price_xpath = '//*[@itemprop="price"]/@content'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_str.append(data[0])
        if len(price_str) == 2:
            item['price'] = self._format_price(price_str[0], price_str[1])

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@id="listPrice"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = ''.join(data[0][len('$'):].split(','))
            item['list_price'] = self._format_price('USD', price_number)

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
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
