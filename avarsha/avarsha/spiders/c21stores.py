# -*- coding: utf-8 -*-
# author: yangxiao

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'c21stores'

class C21storesSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["c21stores.com"]

    def __init__(self, *args, **kwargs):
        super(C21storesSpider, self).__init__(*args, **kwargs)

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
        items_xpath = '//div[@class="primary"]/a/@href'

        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(self.convert_url(item_url))
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = ('//div[@class="pagination wl-cf"]//ul//li/@href |'
            '//div[@class="pagination wl-cf"]/ul/li/a/@href')

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
        title_xpath = '//div[@class="product-info"]/h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'c21stores'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//span[@itemprop="brand"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        item['sku'] = re.search("\"viewItem\", item: \"(.*?)\"", \
            sel.response.body).group(1)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@id="description"]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_list_xpath = '//ul[@class="alternates"]//li//img/@src'
        data = sel.xpath(imgs_list_xpath).extract()
        if len(data) != 0:
            for index in range(len(data)):
                data[index] = data[index].replace('smallThumb', 'superZoom')
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        item['colors'] = re.findall("data-color='{\"NAME\":\"(.*?)\s*\"", \
            sel.response.body)

    def _extract_sizes(self, sel, item):
        item['sizes'] = list(set(re.findall("data-size=.*\"NAME\":\"(.*?)\"", \
            sel.response.body)))

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="price price-sale"]/span[@itemprop="price"]\
            /text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = re.search('\$(.*) \n', data[0]).group(1)
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="price price-original"]/del/span\
            /text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = re.search('\$(.*) \n', data[0]).group(1)
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

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
