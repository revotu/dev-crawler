# -*- coding: utf-8 -*-
# author: yangxiao


import re

import scrapy.cmdline
from scrapy import log
from scrapy.selector import Selector

from avarsha.items import ProductItem
from avarsha_spider import AvarshaSpider


_spider_name = 'shopplanetblue'

class BrooksbrothersSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["shopplanetblue.com"]

    def __init__(self, *args, **kwargs):
        super(BrooksbrothersSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = ('//ul[@class="products-grid"]/li[@class="item"]'
            '/h2[@class="product-name"]/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="pages"]/ol/li/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def parse_item(self, response):
        self.log('Parse item link: %s' % response.url, log.DEBUG)

        sel = Selector(response)
        item = ProductItem()

        # each spider overrides the following methods
        self._extract_url(sel, item)
        self._extract_title(sel, item)
        self._extract_store_name(sel, item)
        self._extract_brand_name(sel, item)
        self._extract_sku(sel, item)
        self._extract_features(sel, item)
        self._extract_description(sel, item)
        self._extract_size_chart(sel, item)
        self._extract_color_chart(sel, item)
        self._extract_image_urls(sel, item)
        self._extract_stocks(sel, item)

        # extract list_price first, then extract price
        self._extract_list_price(sel, item)
        self._extract_price(sel, item)

        self._extract_low_price(sel, item)
        self._extract_high_price(sel, item)
        self._extract_is_free_shipping(sel, item)
        self._extract_review_count(sel, item)
        self._extract_review_rating(sel, item)
        self._extract_best_review_rating(sel, item)
        self._extract_review_list(sel, item)

        # auto filled methods, don't need to override them
        self._save_product_id(sel, item)
        self._record_crawl_datetime(item)
        self._save_product_collections(sel, item)

        # extract colors and sizes at the same time
        self._extract_colors_sizes(sel, item)

        return item

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="product-name"]'
            '/h1[@itemprop="name"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'shopplanetblue'

    def _extract_brand_name(self, sel, item):
        brand_xpath = ('//div[@class="product-main-info"]'
            '/p[@itemprop="brand"]/text()')
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        item['sku'] = re.search('SKU: (.*?)<', sel.response.body).group(1)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//span[@itemprop="description"]/* |'
            '//div[@class="accordrion-content-block"]/div/ul/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//div[@class="MagicToolboxContainer selectorsRight"]'
            '/div[@class="MagicToolboxSelectorsContainer"]/a/@href |'
            '//div[@class="MagicToolboxContainer selectorsRight"]'
            '/div[@class="MagicToolboxMainContainer"]'
            '/div[@class="main-img-container"]/a/@href')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors_sizes(self, sel, item):
        try:
            content = re.search('var spConfig = new Product.Config(.*?);', \
                sel.response.body).group(1)
        except Exception:
            pass
        else:
            label_list = re.findall('"label":"(.*?)"', content)
            try:
                color_index = label_list.index('color')
            except Exception:
                color_index = label_list.index('Color')
            try:
                size_index = label_list.index('size')
            except Exception:
                size_index = label_list.index('Size')
            item['colors'] = label_list[color_index + 1:size_index]
            item['sizes'] = label_list[size_index + 1:]

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        if item.get('list_price') != None:
            price_xpath = ('//p[@class="special-price"]'
            '/span[@class="price"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0].replace('$', '')
                item['price'] = self._format_price("USD", price_number)
        else:
            price_xpath = ('//span[@class="regular-price"]'
                '/span[@class="price"]/span[@itemprop="price"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0]
                item['price'] = self._format_price("USD", price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//p[@class="old-price"]'
            '/span[@class="price"]/text()')
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
