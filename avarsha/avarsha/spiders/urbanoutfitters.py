# -*- coding: utf-8 -*-
# author: yangxiao

import re
import urllib2
import cookielib

import scrapy.cmdline
from scrapy import log
from scrapy.selector import Selector

from avarsha.items import ProductItem
from avarsha_spider import AvarshaSpider


_spider_name = 'urbanoutfitters'

class UrbanoutfittersSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ['urbanoutfitters.com']

    def convert_url(self, url):
        if '#' in url:
            return url[:url.index('#')]
        if ' ' in url:
            return url.replace(' ', '%20')
        else:
            return url

    def __init__(self, *args, **kwargs):
        super(UrbanoutfittersSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.urbanoutfitters.com/urban/catalog/'
        items_xpath = ('//li[@class="product"]//p[@class="product-image"]'
            '/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.urbanoutfitters.com/urban/catalog/category.jsp'
        nexts_xpath = ('//div[@class="category-nav"]'
            '//a[@class="icon icon-RightArrow"]/@href |'
            '//div[@class="pagination"]/span'
            '/a[@class="icon icon-RightArrow"]/@href')

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def parse_item(self, response):
        self.log('Parse item link: %s' % response.url, log.DEBUG)

        sel = Selector(response)
        item = ProductItem()

        # each spider overrides the following methods
        item['url'] = sel.response.url

        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

        item['store_name'] = 'urbanoutfitters'

        sku_xpath = '//meta[@name="productid"]/@content'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

        self._extract_features(sel, item)

        description_xpath = ('//span[@itemprop="description"]/node()')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            while('\n' in data):
                data.remove('\n')
            item['description'] = ''.join(data)

        price_xpath = '//h1[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            sale_price = re.search('(.*) was\((.*)\)', data[0]).group(1)
            main_price = re.search('(.*) was\((.*)\)', data[0]).group(2)
            if '-' in sale_price:
                sale_price = sale_price[:sale_price.index('-') - 1]
            if '-' in main_price:
                main_price = main_price[:main_price.index('-') - 1]
            if sale_price == main_price:
                item['price'] = self._format_price("USD", sale_price)
            else:
                item['price'] = self._format_price("USD", sale_price)
                item['list_price'] = self._format_price("USD", main_price)

        XHR_url = ('http://www.urbanoutfitters.com/api/v1/'
            'product/%s?siteCode=urban' % item['sku'])
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; \
            Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0')]
        content = opener.open(XHR_url).read()

        colors = re.findall('"color":"(.*?)"', content)
        item['colors'] = list(set(colors))

        sizes = re.findall('"size":"(.*?)"', content)
        item['sizes'] = list(set(sizes))

        brand_name = re.search('"brand":"(.*?)"', content).group(1)
        item['brand_name'] = brand_name

        image_codes = re.findall('"viewCode":(.*?),"sizes"', content)
        image_codes = list(set(image_codes))
        image_codes = eval(image_codes[0])

        imgs_list_xpath = '//meta[@property="og:image"]/@content'
        data = sel.xpath(imgs_list_xpath).extract()
        if len(data) != 0:
            data[0] = 'http:' + data[0].replace('detailMain', 'xlarge')
            for code in image_codes:
                image_url = data[0].replace('_b', '_' + code)
                data.append(image_url)
            item['image_urls'] = list(set(data))

        self._extract_size_chart(sel, item)
        self._extract_color_chart(sel, item)

        self._extract_image_urls(sel, item)
        self._extract_stocks(sel, item)
        self._extract_low_price(sel, item)
        self._extract_high_price(sel, item)
        self._extract_is_free_shipping(sel, item)
        self._extract_reviews(sel, item)

        # auto filled methods, don't need to override them
        self._save_product_id(sel, item)
        self._record_crawl_datetime(item)
        self._save_product_collections(sel, item)

        return item

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
