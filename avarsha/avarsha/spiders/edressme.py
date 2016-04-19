# -*- coding: utf-8 -*-
# author fsp

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'edressme'

class EdressmeSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["edressme.com"]

    def __init__(self, *args, **kwargs):
        super(EdressmeSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = ''
        items_xpath = '//div[@class="product-name"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        base_url = ''
        nexts_xpath = '//div[@class="pages"]//a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Edressme'

    def _extract_brand_name(self, sel, item):
        sku_xpath = '//span[@itemprop="brand"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].replace('\t', ' ')\
                .replace('\n', ' ').strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@itemprop="sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].replace('\t', ' ')\
                .replace('\n', ' ').strip()

    def _extract_description(self, sel, item):
        description_xpath = '//span[@itemprop="description"]/text()'
        data = sel.xpath(description_xpath).extract()
        description = ''
        if len(data) != 0:
            description += data[0]
        description = description.replace('  ', '')
        item['description'] = description

    def _extract_image_urls(self, sel, item):
        images_xpath = '//div[@class="more-views"]//a/@href'
        images = sel.xpath(images_xpath).extract()
        if len(images) != 0:
            item['image_urls'] = images

    def _extract_price(self, sel, item):
        price_xpath = '//span[@class="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price = data[0].strip()
            item['price'] = self._format_price('USD', price[len('$'):])

    def _extract_colors(self, sel, item):
        pass
        # TODO:
    def _extract_sizes(self, sel, item):
        pass
        # TODO:

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
