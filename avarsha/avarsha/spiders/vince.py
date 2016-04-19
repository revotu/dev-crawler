# -*- coding: utf-8 -*-
# author: yangxiao


import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'vince'

class VinceSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["vince.com"]

    def __init__(self, *args, **kwargs):
        super(VinceSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//h2[@class="prod-name"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//ul[@class="pagn-pages"]/li/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//meta[@property="og:title"]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Vince'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Vince'

    def _extract_sku(self, sel, item):
        sku_xpath = ('//span[@class="prod-sku"]/text()')
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].replace('SKU: ', '')

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_1_xpath = '//div[@class="content"]/*'
        description_2_xpath = '//div[@class="content des2"]/*'
        data1 = sel.xpath(description_1_xpath).extract()
        data2 = sel.xpath(description_2_xpath).extract()
        data = data1 + data2
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_content = re.findall('imgL: \[\s+([\w\W]*?)\]', sel.response.body)
        img_urls = []
        for i in img_content:
            img_urls += re.findall('"(.+)"', i)
        item['image_urls'] = img_urls

    def _extract_colors(self, sel, item):
        color_xpath = ('//div[@class="row thinpad-top att1row"]'
            '//select[@name="att1"]/option/text()')
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data[1:]

    def _extract_sizes(self, sel, item):
        size_xpath = ('//div[@class="row thinpad-top att2row"]'
            '//select[@name="att2"]/option/text()')
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data[1:]

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@class="prod-pricenow"]/span/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = re.search('\$(.*)', data[0]).group(1)
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//span[@class="prod-price-was"]/span/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = re.search('\$(.*)$', data[0]).group(1)
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
