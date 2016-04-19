# -*- coding: utf-8 -*-
# author: huoda

import json

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'bysymphony'

class BysymphonySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["bysymphony.com"]

    def __init__(self, *args, **kwargs):
        super(BysymphonySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.bysymphony.com'
        items_xpath = '//*[@class="product-name"]/a//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'https://www.bysymphony.com'
        nexts_xpath = '//*[@class="next i-next"][1]//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="main-info"]//*[@itemprop="name"]//text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'bysymphony'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//div[@class="main-info"]//'
            '*[@itemprop="brand"]//text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@name="product"]//@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_description(self, sel, item):
        description_xpath = '//div[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_image_urls(self, sel, item):
        img_xpath = '//*[@class="thumbnails"]//a//@href'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        item['colors'] = ['fasfs']

    def _extract_sizes(self, sel, item):
        sizes = []
        flag = sel.response.body.find('new Product.Config(')
        flag += 19
        flag_end = sel.response.body.find(';', flag)
        text = sel.response.body[flag:flag_end - 1]
        data = json.loads(text)
        for key in data['attributes'].keys():
            v = data['attributes'][key]
            if 'options' in v.keys():
                for itemm in v['options']:
                    size = itemm['label']
                    sizes.append(size)
        item['sizes'] = sizes

    def _extract_price(self, sel, item):
        price_xpath = '//*[@class="regular-price"]/*[@class="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            price_number = price_number[1:]
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = '//*[@class="special-price"]/*[@class="price"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0].strip()
                price_number = price_number[1:]
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@class="old-price"]/*[@class="price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()
            list_price_number = list_price_number[1:]
            item['list_price'] = self._format_price('USD', list_price_number)

    def _extract_is_free_shipping(self, sel, item):
        is_free_shipping_xpath = '//*[@id="shipOpts"]/span/text()'
        data = sel.xpath(is_free_shipping_xpath).extract()
        if len(data) != 0 and data[0] == 'Free':
            item['is_free_shipping'] = True


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
