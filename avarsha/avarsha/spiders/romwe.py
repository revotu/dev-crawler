# -*- coding: utf-8 -*-
# author: yangxiao


import re
import urllib
import urllib2

import scrapy.cmdline
from scrapy import log
from scrapy.selector import Selector

from avarsha.items import ProductItem
from avarsha_spider import AvarshaSpider


_spider_name = 'romwe'

class RomweSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["romwe.com"]

    def __init__(self, *args, **kwargs):
        super(RomweSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = ('//div[@class="products_category"]'
            '/div[@class="box-product-list list_all_items"]'
            '/div[@class="goods_aImg"]/a/@href |'
            '//div[@class="box-product-list list_all_items"]/div[1]/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="pagecurrents2"]/a/@href'

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
        self._extract_colors(sel, item)
        self._extract_sizes(sel, item)
        self._extract_stocks(sel, item)

#         # extract list_price first, then extract price
#         self._extract_list_price(sel, item)
#         self._extract_price(sel, item)

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

        # asynchronous request price and list price
        self._extract_price_and_listprice(sel, item)

        return item

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="goods-content-shopping model-content"]'
            '/h1/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'romwe'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'romwe'

    def _extract_sku(self, sel, item):
        sku_xpath = ('//div[@class="content_sku"]'
            '/span[@id="productCodeSpan"]/text()')
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = (
            '//div[@class="ItemSpecificationCenter goods_description_center"]'
            '/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//div[@class="other_Imgs"]/a/div/img/@data-src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        if len(item['description']) != 0:
            for i in item['description']:
                if re.search('^Color :(.*)$', i) != None:
                    item['colors'] = re.search('^Color :(.*)$', i).group(1)

    def _extract_sizes(self, sel, item):
        size_xpath = '//ul[@class="choose_size"]/li/text()'
        size_list = sel.xpath(size_xpath).extract()
        if len(size_list) != 0:
            item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price_and_listprice(self, sel, item):
        goods_id = re.search('-(\d+)-', sel.response.url).group(1)
        url = 'http://www.romwe.com/index.php'
        form_data = {
            'model':'product',
            'action':'update_product_price',
            'goods_id':goods_id,
            'change_currency_update':'1'}
        params = urllib.urlencode(form_data)
        response = urllib2.urlopen(url, params)
        data = response.read()
        price_number = re.search('"shop_price":"(.*?)"', data).group(1)
        item['list_price'] = self._format_price("USD", price_number)
        price_number = re.search('"unit_price":"(.*?)"', data).group(1)
        item['price'] = self._format_price("USD", price_number)

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
