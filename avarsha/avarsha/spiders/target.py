# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

import urllib2

import math

import re

from avarsha_spider import AvarshaSpider


_spider_name = 'target'

class TargetSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["target.com"]

    def __init__(self, *args, **kwargs):
        super(TargetSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if idx1 != -1:
            return url[:idx1]
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        if sel.response.url.find('s?searchTerm=') != -1:
            items_xpath = '//a[contains(@class, "productClick")]/@href'
            data = sel.xpath(items_xpath).extract()
            requests = []
            for path in data:
                idx = path.find('#')
                if idx != -1:
                    item_url = path[:idx]
                else:
                    item_url = path
                requests.append(
                    scrapy.Request(url=item_url, callback=self.parse_item))
                item_urls.append(item_url)
            return requests
        else:
            idx1 = sel.response.url.rfind('-')
            if idx1 == -1:
                return []
            category = sel.response.url[idx1 + 1:]
            first_page_url = ('http://tws.target.com/searchservice/item/'
                'search_results/v1/by_keyword?callback=getPlpResponse&category'
                '=%s&pageCount=30&page=1' % category)
            request = urllib2.Request(first_page_url)
            response = urllib2.urlopen(request)
            maxpage = 1
            while True:
                try:
                    body = response.read().split(',{')
                    break
                except:
                    continue

            for line in body:
                idx2 = line.find('prodCount\",\"value\":\"')
                if idx2 != -1:
                    idx3 = line.find('\"}', idx2)
                    if idx3 != -1:
                        count = int(line[idx2 + \
                            len('prodCount\",\"value\":\"'):idx3].strip())
                        maxpage = int(math.ceil(count / (30.0)))
                        break

            requests, page = [], 1
            while page <= maxpage:
                page_url = ('http://tws.target.com/searchservice/item/'
                'search_results/v1/by_keyword?callback=getPlpResponse&category'
                '=%s&pageCount=30&page=%d' % (category, page))
                request = urllib2.Request(page_url)
                response = urllib2.urlopen(request)
                try:
                    body = response.read().split(',')
                except:
                    continue
                for line in  body:
                    idx1 = line.find('productDetailPageURL\":\"')
                    if idx1 != -1:
                        idx2 = line.find('\",', idx1)
                        item_url = 'http://www.target.com/' + line[idx1 \
                            + len('productDetailPageURL\":\"'):idx2]
                        item_urls.append(item_url)
                        requests.append(scrapy.Request(item_url,
                            callback=self.parse_item))
                page += 1
            # don't need to change this line
            return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        if sel.response.url.find('s?searchTerm=') != -1:
            base_url = 'http://www.target.com'
            nexts_xpath = '//ul[@class="lpPagination"]//li/a/@href'
            return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)
        else:
            return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h2[@class="product-name item"]/span/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            idx1 = data[0].rfind('-')
            if idx1 != -1:
                brand_str = data[0][:idx1]
                item['title'] = brand_str.strip()
            else:
                idx2 = data[0].find(u'\xae')
                if idx2 != -1:
                    item['title'] = data[0][idx2 + 1:].strip()
                else:
                    idx3 = data[0].find('/')
                    if idx3 != -1:
                        item['title'] = data[:idx3]
                    else:
                        item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Target'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '////h2[@class="product-name item"]/span/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            idx1 = data[0].rfind('-')
            if idx1 != -1:
                brand_str = data[0][idx1 + 1:]
                item['brand_name'] = brand_str.strip()
            else:
                idx2 = data[0].find(u'\xae')
                if idx2 != -1:
                    item['brand_name'] = data[0][:idx2]
                else:
                    idx3 = data[0].find('/')
                    if idx3 != -1:
                        item['brand_name'] = data[idx3 + 1:]
                    else:
                        item['brand_name'] = 'Target'

    def _extract_sku(self, sel, item):
        sku_xpath = '//input[@id="zoomProductPartNum"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//ul[@class="normal-list"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line.strip()
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        num_url = sel.response.url
        num = num_url[num_url.rfind('-') + 1:]
        imgs.append('http://scene7.targetimg1.com/is/image/Target/' \
                    + num + '?scl=1')
        imgs.append('http://scene7.targetimg1.com/is/image/Target/' \
                    + num + '_Alt01?scl=1')
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        colors_xpath = (
            '//ul[@class="swatches"]//li[@class="swatchtool"]/input/@alt')
        data = sel.xpath(colors_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//select[@class="sizeSelection"]//option/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            size_list = data[1:]
            if len(size_list) != 0:
                item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//p[@class="price"]/span[@class="offerPrice"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = str(
                re.search(re.compile(r'\d+\.?\d+'), data[0]).group())
            item['price'] = self._format_price('USD ', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//li[@id="regPriceDisplay"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            match = re.search(re.compile(r'\d+\.?\d+'), data[0])
            if match != None:
                price_number = str(match.group())
                item['list_price'] = self._format_price('USD', price_number)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        is_free_shipping_xpath = (
            '//li[@class="shippingPrmLi"]/p[@class="shpPrmMsg"]/text()')
        data = sel.xpath(is_free_shipping_xpath).extract()
        if len(data) != 0 and data[0].strip() == 'SHIPS FREE':
            item['is_free_shipping'] = True

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
