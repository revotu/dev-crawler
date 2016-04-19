# -*- coding: utf-8 -*-
# @author: huangjunjie
import urllib2, re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'theory'

class TheroySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["theory.com"]

    def __init__(self, *args, **kwargs):
        super(TheroySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.theory.com'
        items_xpath = '//*[@class="product_name"]/a/@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="productname"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Theroy'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Theroy'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="itemNo productid grid_4"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            sku = data[0].strip()
            sku = sku.split(" ")[2]
            item['sku'] = sku


    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="shortDescription"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            description = data[len(data) - 1]
            description_xpath2 = '//div[@class="longDescription"]'
            data2 = sel.xpath(description_xpath2).extract()
            if len(data2) != 0:
                description = description + data2[0]
            item['description'] = description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//div[@id="s7container"]//img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            src0 = data[0]
            index = src0.rfind('0')
            jsonsrc = src0[:index] + 's' + src0[index + 1:] + '&req=imageset,json'
            html = urllib2.urlopen(jsonsrc).read()
            index2 = html.find('(')
            html = html[index2:-1]
            html = tuple(eval(html))
            html = html[0]['IMAGE_SET']
            src1 = re.split(';|,', html)
            src0 = src0[:src0.rfind('/Theory') + 1]
            for tmp in src1:
                imgs.append(src0 + tmp)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//div[contains(@class, "color")]//ul/li/a/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data


    def _extract_sizes(self, sel, item):
        size_xpath = '//div[contains(@class, "size")]//ul/li/a/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@class="price"]'
            '//span[contains(@class,"salesprice")]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath2 = '//span[@class="pricing"]/span[@class="price"]'
            data2 = sel.xpath(price_xpath2).extract()
            price_number = re.search(r'\$(?P<price>.*)-', data[0])
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="standardprice"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
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
