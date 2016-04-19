# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re
import time
import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'coggles'

class CogglesSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["coggles.com"]
    has_items = True

    def __init__(self, *args, **kwargs):
        super(CogglesSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if(idx1 != -1):
            idx2 = url.find('.com')
            idx3 = url.find('?search=')
            idx4 = url.find('#!|')
            _pre = 'http://www.coggles.com/searchRequest.facet?'
            _parameters = ''
            _sectionName = ''
            _vars = []
            _vars2 = []
            _facetCriteria = ''
            _pageNumber = 1
            _productsPerPage = 66
            _searchType = ''
            _searchTerm = ''
            _now = time.time()
            _parameters_quote = ''
            if(idx3 != -1):
                _sectionName = url[idx2 + len('.com'):idx3]
                _productsPerPage = 21
                _searchType = 'search'
                _searchTerm = url[idx3 + len('?search='):idx1]
            else:
                _sectionName = url[idx2 + len('.com'):idx1]
                _searchType = 'list'
            _vars = url[idx4 + len('#!|'):].split('|')
            for _var in _vars:
                _vars2.append('"' + _var.replace(' ', '+') + '"')
            _facetCriteria = ','.join(_vars2)
            _var1 = 'facetItemsJson={"sectionName":"'
            _var2 = '","facetCriteria":['
            _var3 = '],"pageNumber":"'
            _var4 = '","productsPerPage":'
            _var5 = ',"sortField":"","searchType":"'
            _var6 = '","searchTerm":"'
            _var7 = ('","department":"","categoryLevel1":"",'
                '"categoryLevel2":"","categoryLevel3":""}')
            _var8 = '&_='
            _parameters = _var1 + _sectionName + _var2 + _facetCriteria + \
                _var3 + str(_pageNumber) + _var4 + str(_productsPerPage) + \
                _var5 + _searchType + _var6 + _searchTerm + _var7
            _parameters_quote = urllib2.quote(
                _parameters.encode('utf-8'), "?=+")
            url = _pre + _parameters_quote + _var8 + str(_now)
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        _url = sel.response.url
        if(_url.find('facetItemsJson') != -1):
            line = sel.response.body
            while(True):
                idx1 = line.find('"url":"')
                if(idx1 != -1):
                    idx2 = line.find('",', idx1)
                    item_url = line[idx1 + len('"url":"'):idx2]
                    item_urls.append(item_url)
                    request = scrapy.Request(item_url, callback=self.parse_item)
                    requests.append(request)
                    line = line[idx2:]
                else: break
        else:
            base_url = ''
            items_xpath = ('//div[@id="divSearchResults"]//'
                'p[@class="product-name"]/a/@href')
            item_nodes = sel.xpath(items_xpath).extract()
            for path in item_nodes:
                item_url = path
                if path.find(base_url) == -1:
                    item_url = base_url + path
                item_urls.append(item_url)
                request = scrapy.Request(item_url, callback=self.parse_item)
                requests.append(request)
        if(requests == []):
            self.has_items = False
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        if(self.has_items == False):
            return requests
        list_url = ''
        _url = sel.response.url
        idx = _url.find('facetItemsJson')
        if(idx != -1):
            _pre = 'http://www.coggles.com/searchRequest.facet?'
            _parameters = _url[idx:]
            _parameters = urllib2.unquote(_parameters.encode('utf-8'))
            idx1 = _parameters.find('pageNumber":"')
            idx2 = _parameters.find('",', idx1)
            _pageNumber = _parameters[idx1 + len('pageNumber":"'):idx2]
            _pageNumber = str(int(_pageNumber) + 1)
            _parameters = _parameters[:idx1 + len('pageNumber":"')] + \
                _pageNumber + _parameters[idx2:]
            _parameters = urllib2.quote(_parameters.encode('utf-8'), "?=&+")
            list_url = _pre + _parameters
        else:
            base_url = sel.response.url
            idx = base_url.find('?')
            if(idx != -1):
                base_url = base_url[:idx]
            nexts_xpath = '//div[@class="next"]/a/@href'
            nexts = sel.xpath(nexts_xpath).extract()
            if(len(nexts) != 0):
                list_url = base_url + nexts[0]
        list_urls.append(list_url)
        request = scrapy.Request(list_url, callback=self.parse)
        requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'COGGLES'

    def _extract_brand_name(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]/text()'
        _title = sel.xpath(title_xpath).extract()
        brand_name_xpath = '//p[@class="product-brand"]/text()'
        _brand_name = sel.xpath(brand_name_xpath).extract()
        if (len(_title) != 0 and len(_brand_name) != 0):
            for line in _brand_name:
                if(_title[0].find(line) != -1):
                    item['brand_name'] = line
        else:
            item['brand_name'] = 'COGGLES'

    def _extract_sku(self, sel, item):
        for line in sel.response.body.split('\n'):
            idx1 = line.find("'productSKU':'")
            if(idx1 != -1):
                idx2 = line.find("'", idx1 + len("'productSKU':'"))
                item['sku'] = line[idx1 + len("'productSKU':'"):idx2]

    def _extract_features(self, sel, item):
        features_xpath = '//div[@class="product-more-details"]'
        data = sel.xpath(features_xpath).extract()
        _features = {}
        _name = ''
        _value = ''
        if len(data) != 0:
            line = data[0]
            while(True):
                idx1 = line.find('<th>')
                if(idx1 != -1):
                    idx2 = line.find('</th>', idx1 + len('<th>'))
                    _name = line[idx1 + len('<th>'):idx2]
                    data_re = re.compile(r'(?:<[^<>]+>)|\n+|\t+|\r+|  +|[:]')
                    _name = data_re.sub('', _name).strip()
                    line = line[idx2:]
                    idx1 = line.find('<li>')
                    if(idx1 != -1):
                        idx2 = line.find('</li>', idx1 + len('<li>'))
                        _value = line[idx1 + len('<li>'):idx2]
                        data_re = re.compile(r'(?:<[^<>]+>)|\n+|\t+|\r+|  +')
                        _value = data_re.sub('', _value).strip()
                        _features[_name] = _value
                        line = line[idx2:]
                else:
                    break
        item['features'] = _features

    def _extract_description(self, sel, item):
        description_xpath = '//div[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_url_xpath = '//ul[@class=\
            "product-thumbnails nav-items product-large-view-thumbs"]//a/@href'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        if(len(data_imgs) != 0):
            item['image_urls'] = data_imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//p[@class="product-price"]/span[@class="price"]/text()'
        price = sel.xpath(price_xpath).extract()
        if(len(price) != 0):
            data_re = re.compile(r'\n+|\t+|\r+| +|&#163;|\xa3|[$£]')
            item['price'] = self._format_price(
                'GBP', data_re.sub('', price[0]).strip())

    def _extract_list_price(self, sel, item):
        saving_percent_xpath = '//p[@class="yousave saving-percent"]'
        saving_percent = sel.xpath(saving_percent_xpath).extract()
        if(len(saving_percent) != 0):
            for line in sel.response.body.split('\n'):
                idx1 = line.find('class="strike">&#163;|\xa3|[$£]')
                if(idx1 != -1):
                    idx2 = line.find('</span>', idx1)
                    list_price = line[idx1 + len('class="strike">&#163;'):idx2]
                    item['list_price'] = self._format_price('GBP', list_price)
                    break

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
