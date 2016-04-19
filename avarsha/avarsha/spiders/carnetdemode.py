# -*- coding: utf-8 -*-
# author: tanyafeng

import re
import urllib
import urllib2
import math
import json

import scrapy.cmdline
from scrapy import log
from scrapy.http import FormRequest

from avarsha_spider import AvarshaSpider


_spider_name = 'carnetdemode'

class CarnetdemodeSipder(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["carnetdemode.com"]

    def __init__(self, *args, **kwargs):
        super(CarnetdemodeSipder, self).__init__(*args, **kwargs)

    def find_nexts_from_list_page(self, sel, list_urls):
        requests = []
        total = 0.0
        max_page = 1
        post_paras = []
        post_data = {}
        query_str = ''
        post_url = 'http://en.carnetdemode.com/design/list'
        category_pattern = re.compile('categories\\W*(\\d*)')
        sex_pattern = re.compile('sexes\\W*(\\d*)')
        for line in sel.response.body.split('\n'):
            if line.find('goSearchFilters') != -1:
                match = category_pattern.findall(line)
                if len(match) != 0:
                    post_paras.append(match[0])
                match = sex_pattern.findall(line)
                if len(match) != 0:
                    post_paras.append(match[0])
                break

        if len(post_paras) == 2:
            post_data = {'filters[categories][]':post_paras[0], \
                'filters[sexes][]':post_paras[1], 'page':'0', \
                'sort':'-5', 'resultsPerPage':'24'}
        else:
            idx = sel.response.url.find('search/')
            if idx != -1:
                query_str = sel.response.url[idx + len('search/'):]
                post_data = {'query' : query_str , 'page' : '0', \
                    'sort' : '-1', 'resultsPerPage' : '24'}
        if len(post_data) != 0:
            post_data_encode = urllib.urlencode(post_data)
            req = urllib2.Request(url = post_url, data = post_data_encode)
            list_response = urllib2.urlopen(req)
            dict_data = json.loads(list_response.read().decode('UTF-8'))
            total = float(dict_data["data"]["total"])
            max_page = int(math.ceil(total / 24.0))
            if max_page > 1:
                for page_num in range(0, max_page):
                    self.log('Parse category pagenum: %d' % page_num, log.DEBUG)
                    if len(post_paras) == 2:
                        post_data = {'filters[categories][]':post_paras[0], \
                            'filters[sexes][]':post_paras[1], 'page':\
                            str(page_num), 'sort':'-5', 'resultsPerPage':'24'}
                    else:
                        post_data = {'query' : query_str , 'page' : \
                            str(page_num) , 'sort' : '-1', \
                            'resultsPerPage' : '24'}
                    request = FormRequest(post_url,
                        formdata = post_data,
                        callback = self.parse
                        )
                    list_urls.append(post_url)
                    requests.append(request)
        return requests

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        """the result format is json"""

        requests = []
        base_url = 'http://en.carnetdemode.com/design'
        if sel.response.body.find('"total":') != -1:
            dict_data = json.loads(sel.response.body)
            results = dict_data['data']['results']
            for items in results:
                design_tag = items['design']['URLTag']
                main_color_tag = items['mainColor']['URLTag']
                item_url = '%s/%s/%s' % (base_url, design_tag, main_color_tag)
                item_urls.append(item_url)
                requests.append(scrapy.Request(item_url, callback = \
                    self.parse_item))
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@class="design"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Carnetdemode'

    def _extract_brand_name(self, sel, item):
        brand_pattern = re.compile('product_brand\\W*"(.*?)"')
        for line in sel.response.body.split('\n'):
            if line.find('product_brand') != -1:
                match = brand_pattern.findall(line)
                if len(match) != 0:
                    item['brand_name'] = match[0]
                break

    def _extract_sku(self, sel, item):
        sku_pattern = re.compile('product_id.*?"(.*?)"')
        for line in sel.response.body.split('\n'):
            if line.find('product_id') != -1:
                match = sku_pattern.findall(line)
                if len(match) != 0:
                    item['sku'] = match[0]
                break

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//*[@class="panel-collapse in hidden-xs"]'
            '/div/node()')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        base_url = 'http://en.carnetdemode.com'
        img_xpath = '//*[@data-zoom-image]/@data-image'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            for img_str in data:
                imgs.append(base_url + img_str)
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        data = sel.response.url.split('/')
        item['colors'] = [data[len(data) - 1]]

    def _extract_sizes(self, sel, item):
        sizes = []
#         size_xpath = '//*[@id="size-select"]/option/text()'
        size_xpath = '//*[@class="heading"]/td/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            for size_str in data:
                if size_str.find('stock') == -1:
                    size_strs = size_str.strip().split(' ')
                    sizes.append(size_strs[len(size_strs) - 1])
            item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_str = []
        currency_pattern = re.compile('currency\\W*"(.*?)"')
        price_pattern = re.compile('product_price\\W*"(.*?)"')
        for line in sel.response.body.split('\n'):
            if line.find('var currency') != -1:
                match = currency_pattern.findall(line)
                price_str.append(match[0])
                break
        for line in sel.response.body.split('\n'):
            if line.find('product_price') != -1:
                match = price_pattern.findall(line)
                price_str.append(match[0])
                break
        if len(price_str) == 2:
            item['price'] = self._format_price(price_str[0], price_str[1])

    def _extract_list_price(self, sel, item):
        price_str = []
        currency_pattern = re.compile('currency\\W*"(.*?)"')
        price_pattern = re.compile('product_oldprice\\W*"(.*?)"')
        for line in sel.response.body.split('\n'):
            if line.find('var currency') != -1:
                match = currency_pattern.findall(line)
                price_str.append(match[0])
                break
        for line in sel.response.body.split('\n'):
            if line.find('product_oldprice') != -1:
                match = price_pattern.findall(line)
                price_str.append(match[0])
                break
        if len(price_str) == 2:
            item['list_price'] = self._format_price(price_str[0], price_str[1])

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
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
