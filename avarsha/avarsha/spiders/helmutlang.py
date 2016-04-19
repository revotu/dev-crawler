# -*- coding: utf-8 -*-
# @author: huangjunjie
import urllib2, re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'helmutlang'

class HelmutlangSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["helmutlang.com"]

    def __init__(self, *args, **kwargs):
        super(HelmutlangSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.helmutlang.com'
        items_xpath = '//*[@class="thumbnail"]/a/@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[contains(@class,"productname")]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Helmutlang'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Helmutlang'

    def _extract_sku(self, sel, item):
        url = sel.response.url
        index = url.rfind('/')
        url = url[index:]
        m = re.search(r'\/(?P<sku>.*),default', url)
        if m:
            item['sku'] = m.groupdict('sku')['sku']


    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//*[@class="hl_productDescription"]/text()'
            '|//div[@class="hl_productDetailsContainer"]//ul[not(@style)]')
        data = sel.xpath(description_xpath).extract()
        desc = ''
        if len(data) != 0:
            for i in range(len(data)):
                desc = desc + data[i].strip()
        item['description'] = desc


    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_path = '//img[@id="productImage"]/@src'
        data = sel.xpath(img_path).extract()
        imgs = []
        if len(data) != 0:
            src0 = data[0]
            index0 = src0.rfind('P0')
            src1 = src0[:index0] + 's' + '?&req=imageset,json'
            html = urllib2.urlopen(src1).read()
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
        color_xpath = ('//div[@class="swatches  color"]/'
            'div[@class="grid_7"]//ul/li/a/text()')
        data = sel.xpath(color_xpath).extract()

        if len(data) != 0:
            item['colors'] = data


    def _extract_sizes(self, sel, item):
        size_xpath = ('//div[@class="swatches long  size"]'
            '/div[@class="grid_7"]//ul/li/a/text()')
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[contains(@class,"price")]'
            '//span[contains(@class,"salesprice")]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[contains(@class,"price")]'
            '//span[@class="standardprice"]/text()')
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
