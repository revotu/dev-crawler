# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

from scrapy import log

import json

import urllib2

from scrapy.http import FormRequest

from avarsha_spider import AvarshaSpider


_spider_name = 'vestiairecollective'

class VestiairecollectiveSpider(AvarshaSpider):
    name = _spider_name
    allow_domains = ["vestiairecollective.com"]
    def __init__(self, *args, **kwargs):
        self.email = 'zzhangliangliang@gmail.com'
        self.pwd = 'liang1993'
        self.headers = {
            'Cookie' : '__troRUID=9eec7ed4-9988-4e88-92f5-1cb324436492; __sonar=8717925273908362173; __troSYNC=1; tc_cj_v2=%5Ecl_%5Dny%5B%5D%5D_mmZZZZZZKNMNJRRMJOKQNZZZ%5D; vc_rid=_xD46rJ6WZ5QAGPu_LzpE0SBCjVMKinW; vc_ck=6.en.USD; vc_cc=eyJDQyI6IlVTIiwiZGlzcGxheU5hbWUiOnsiZnIiOiJFdGF0cy1VbmlzIiwiZW4iOiJVbml0ZWQgU3RhdGVzIiwiZGUiOiJVU0EiLCJ1cyI6bnVsbCwiaXQiOiJTdGF0aSBVbml0aSIsImVzIjoiRXN0YWRvcyBVbmlkb3MifX0; _gat=1; test_ab=42; flags=eyJkaXNwbGF5UG9waW4yVmlld3MiOnsidmFsdWUiOjUsImV4cGlyZXMiOjE0MzQxNzUzODI2OTZ9fQ; __55={"st":"regular","ms":"non-member","vF0":1433727713530,"vF":"occasional","vF1":1434082270054}; _ga=GA1.2.297696359.1433727714; stc111485=env:1434088055%7C20150713054735%7C20150612063303%7C4%7C1012567:20160611060303|uid:1434082270898.342301015.111485.2126708791.5:20160611060303|srchist:1012567%3A1434088055%3A20150713054735:20160611060303|tsa:1434088055909.242671700.6302842102013528.874338444:20150612063303; rCookie=9ipf61mcehf1dcxqhcz1e51e2qsq0k',
            'Host' : 'api.vestiairecollective.com',
            'Origin' : 'http://www.vestiairecollective.com',
            'Referer' : 'http://www.vestiairecollective.com/?bye',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'
        }
        super(VestiairecollectiveSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        request = FormRequest('https://api.vestiairecollective.com/',
            formdata={
                'm' : 'userLogin',
                'a' : 'int_js',
                'h' : '5fcdc0ac04537595a747e2830037cca0',
                'u' : '4stor',
                'v' : '1',
                'lang' : 'en',
                'currency' : 'USD',
                'id_site' : '6',
                'email' : self.email,
                'password' : self.pwd},
            callback=self.after_login,
            headers=self.headers
            )
        return [request]

    def after_login(self, response):
        self.log('Login to vestiairecollective successfully', log.DEBUG)
        requests = []
        for s_url in self.start_urls:
            requests.append(scrapy.Request(url=s_url, callback=self.parse))
        return requests

    def convert_url(self, url):
        idx = url.find('#')
        idx1 = url.find('search/?q=')
        if idx != -1 and idx1 != -1:
            self.search_str = '&search=' + url[idx1 + len('search/?q='):idx]
            self.sel_str = url[idx + 1:]
            idx2 = self.sel_str.find('_=catalog&')
            if idx2 != -1:
                self.sel_str = self.sel_str[idx2 + len('_=catalog&'):] + '&'
            else:
                self.sel_str = ''
            return url[:idx]
        elif idx1 != -1:
            self.sel_str = ''
            self.search_str = '&search=' + url[idx1 + len('search/?q='):]
            return url
        elif idx != -1:
            self.search_str = ''
            self.sel_str = url[idx + 1:]
            idx2 = self.sel_str.find('_=catalog&')
            if idx2 != -1:
                self.sel_str = self.sel_str[idx2 + len('_=catalog&'):] + '&'
            else:
                self.sel_str = ''
            return url[:idx]
        self.sel_str = ''
        self.search_str = ''
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        id_page_xpath = '//input[@name="id_page"]/@value'
        data = sel.xpath(id_page_xpath).extract()
        if len(data) != 0:
            id_page = 'id_page=' + data[0].strip() + '&'
        else:
            id_page = ''
        base_url = 'http://www.vestiairecollective.com/'
        limit = 0
        requests = []
        while True:
            category_url = ('http://www.vestiairecollective.com/api/'
                '?m=listProduct&a=int_js&h=5fcdc0ac04537595a747e2830037cca0'
                '&u=4stor&v=1&lang=en&currency=USD&id_site=6%s'
                '&limit=%d&fast=fast&%s%sstep=60' \
                % (self.search_str, limit, self.sel_str, id_page))
            request = urllib2.Request(category_url)
            data = json.loads(urllib2.urlopen(request).read())
            total = int(data['result']['nbProduct'])
            listProduct = data['result']['listProduct']
            for product in listProduct:
                item_url = base_url + product['ezlink'] + '.shtml'
                item_urls.append(item_url)
                requests.append(scrapy.Request(item_url, \
                    callback=self.parse_item))
            if limit + 60 >= total:
                break
            limit += 60
        return requests


    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="prd-title"]/span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Vestiairecollective'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = (
            '//h1[@class="prd-title"]/span[@itemprop="brand"]/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//input[@name="productID"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//li[@id="productDescription"]'
            '/div[@class="details in clear"]//ul//li//text()')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line.strip() + ' '
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        image_xpath = ('//div[@id="prd_gallery"]'
            '/div[@id="in"]/ul//li/button/@data-src-zoom')
        data = sel.xpath(image_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//li[@id="couleur"]/text()'
        data = sel.xpath(color_xpath).re('\w+')
        if len(data) == 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//span[@id="size"]/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            idx = 0
            while idx < len(data):
                data[idx] = data[idx].strip()
                idx += 1
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@class="prd-price-amounts"]'
            '/strong[@id="actual_price_old"]/text()')
        price1_xpath = ('//span[@class="prd-price-amounts"]'
            '/ins[@id="actual_price_new"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)
        else:
            data = sel.xpath(price1_xpath).extract()
            if len(data) != 0:
                price_number = data[0][len('$'):].strip()
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="prd-price-amounts"]/del/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0][len('$'):].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

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

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
