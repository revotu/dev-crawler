# -*- coding: utf-8 -*-
# author: yangxiao


import re

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'nancymeyer'

class NancymeyerSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["nancymeyer.com"]

    def __init__(self, *args, **kwargs):
        super(NancymeyerSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//a[@rapt="SearchProduct"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.nancymeyer.com/'
        nexts_xpath = '//a[@class="SitePath Pager"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@class="prod-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'nancymeyer'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//span[@class="prod-brand"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0][:-1]

    def _extract_sku(self, sel, item):
        item['sku'] = re.search('/([A-Z]+)/', sel.response.url).group(1)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="description"]/span/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_cur_xpath = '//img[@id="MainImage"]/@src'
        data = sel.xpath(imgs_cur_xpath).extract()
        if len(data) != 0:
            image_urls = data
        imgs_alt_xpath = '//div[@class="left"]/a[@class="altLink"]/@onclick'
        data = sel.xpath(imgs_alt_xpath).extract()
        if len(data) != 0:
            try:
                data = [re.search("AlternateClick\('(.*)?',", i)\
                    .group(1) for i in data]
                image_urls.extend(data)
            except:
                self.log('Fail to download some pictures.', log.DEBUG)
        item['image_urls'] = \
            ['http://www.nancymeyer.com/' + i for i in image_urls ]

    def _extract_colors(self, sel, item):
        color_xpath = '//div[@class="ATTR_Attribute"]/select/option/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data[1:]

    def _extract_sizes(self, sel, item):
        size_xpath = '//div[@class="ATTR_Size"]/select/option/text()'
        size_list = sel.xpath(size_xpath).extract()
        if len(size_list) != 0:
            item['sizes'] = size_list[1:]

    def _extract_stocks(self, sel, item):
        pass

    def _extract_prices(self, sel, item):
        self._extract_list_price(sel, item)
        self._extract_price(sel, item)
        self._extract_low_price(sel, item)
        self._extract_high_price(sel, item)

    def _extract_price(self, sel, item):
        if item.get('list_price') == None:
            price_xpath = ('//span[@class="ProductPricing"]'
                '/span[@class="ListPricewoSale"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0].replace('$', '')
                item['price'] = self._format_price("USD", price_number)
        else:
            price_xpath = ('//span[@class="ProductPricing"]'
                '/span[@class="SalePrice"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = re.search('(\$.*)$', data[-1]).group(1)\
                    .replace('$', '')
                item['price'] = self._format_price("USD", price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//span[@class="ProductPricing"]'
            '/span[@class="ListPricewSale"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].replace('$', '')
            item['list_price'] = self._format_price("USD", price_number)

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
