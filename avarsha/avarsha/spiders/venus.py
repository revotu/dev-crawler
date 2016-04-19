# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import cookielib
import socket
import urllib2

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'venus'

class VenusSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["venus.com"]

    def __init__(self, *args, **kwargs):
        super(VenusSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@class="product-text"]/a[1]/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        __productinfo = self.__try_extract_productinfo(sel)
        idx1 = __productinfo.find('"Name":"')
        if(idx1 != -1):
            idx2 = __productinfo.find('","', idx1)
            __title = __productinfo[idx1 + len('"Name":"'):idx2]
        item['title'] = __title

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Venus'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Venus'

    def _extract_sku(self, sel, item):
        for line in sel.response.body.split('\n'):
            idx1 = line.find('"StyleNumber":"')
            if idx1 != -1:
                idx2 = line.find('",', idx1)
                sku = line[idx1 + len('"StyleNumber":"'):idx2].strip()
                break
        item['sku'] = str(sku)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description = []
        description_str, description_main, description_body = \
            self.__pre_description(sel.response)
        content = self.__construct_XHR(description_str)
        content = self.__remove_escape(content)
        idx1 = content.find('{"d":"')
        if idx1 != -1:
            idx2 = content.find('"}', idx1)
            more_detail_str = content[idx1 + len('{"d":"') : idx2].strip()
        description.append(description_main)
        description.append(description_body)
        description.append(more_detail_str)
        item['description'] = ' '.join(str(v) for v in description)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        image_urls = []
        image_urls_str = ''
        for line in sel.response.body.split('\n'):
            idx1 = line.find('"AlternateImages":[')
            if idx1 != -1:
                idx2 = line.find(']', idx1)
                image_urls_str = \
                    line[idx1 + len('"AlternateImages":[') : idx2 + 1].strip()
                break
        while(True):
            idx1 = image_urls_str.find('"')
            if idx1 != -1:
                idx2 = image_urls_str.find('"', idx1 + 1)
                image_url = image_urls_str[idx1 + len('"'):idx2].strip()
                image_urls.append(''.join(
                    ['http://image.venusswimwear.com/is/image/Venus/', \
                        image_url, '?$ProductPage527x738$']))
                image_urls_str = image_urls_str[idx2 + 1:]
            else:
                break
        item['image_urls'] = image_urls

    def _extract_colors(self, sel, item):
        color_set = set()
        color_str = ''
        for line in sel.response.body.split('\n'):
            idx1 = line.find('"Colors":')
            if idx1 != -1:
                idx2 = line.find(']', idx1)
                color_str = line[idx1:idx2].strip()
                break
        while(True):
            idx1 = color_str.find('"LabelText":"')
            if idx1 != -1:
                idx2 = color_str.find('",', idx1)
                color = color_str[idx1 + len('"LabelText":"'):idx2].strip()
                color_set.add(color)
                color_str = color_str[idx1 + len('"LabelText":"'):]
            else:
                break
        item['colors'] = list(color_set)

    def _extract_sizes(self, sel, item):
        size_set = set()
        size_str = ''
        for line in sel.response.body.split('\n'):
            idx1 = line.find('"Sizes":')
            if idx1 != -1:
                idx2 = line.find(']', idx1)
                size_str = line[idx1:idx2].strip()
                break
        while(True):
            idx1 = size_str.find('"ID":"')
            if idx1 != -1:
                idx2 = size_str.find('",', idx1)
                size = size_str[idx1 + len('"ID":"'):idx2].strip()
                size_set.add(size)
                size_str = size_str[idx1 + len('"ID":"'):]
            else:
                break
        item['sizes'] = list(size_set)

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        __productinfo = self.__try_extract_productinfo(sel)
        idx0 = __productinfo.find('"BasePrice":"')
        idx1 = __productinfo.find('"SalePrice":"')
        if idx0 != -1 and idx1 == -1:
            idx2 = __productinfo.find('","', idx0)
            price = __productinfo[idx0 + len('"BasePrice":"'):idx2].strip()
            item['price'] = self._format_price('USD', price)
        elif idx0 != -1 and idx1 != -1:
            idx2 = __productinfo.find('","', idx1)
            price = __productinfo[idx1 + len('"SalePrice":"'):idx2].strip()
            item['price'] = self._format_price('USD', price)

    def _extract_list_price(self, sel, item):
        __productinfo = self.__try_extract_productinfo(sel)
        idx0 = __productinfo.find('"BasePrice":"')
        idx1 = __productinfo.find('"SalePrice":"')
        if idx0 != -1 and idx1 != -1:
            idx2 = __productinfo.find('","', idx0)
            list_price = __productinfo[idx0 + len('"BasePrice":"'):idx2].strip()
            item['list_price'] = self._format_price('USD', list_price)

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

    def __remove_escape(self, content):
        content = content.replace('\\u003cBR\\u003e', ', ')
        return content

    def __pre_description(self, response):
        description_str = ''
        for line in response.body.split('\n'):
            idx1 = line.find('"ProductList":')
            if idx1 != -1:
                idx2 = line.find(']', idx1)
                description_str = line[idx1 + \
                    len('"ProductList":') : idx2 + 1].strip()
                break
        idx1 = description_str.find('"MainDescription":"')
        if idx1 != -1:
            idx2 = description_str.find('",', idx1)
            description_main = description_str[idx1 + \
                len('"MainDescription":"'):idx2].strip()
        idx1 = description_str.find('"Descriptions":')
        if idx1 != -1:
            idx2 = description_str.find(']', idx1)
            description_body = \
                description_str[idx1 + len('"Descriptions":') \
                + 1:idx2].strip().replace('"', '')

        return description_str, description_main, description_body

    def __construct_XHR(self, description_str):
        more_detail_url = ('http://www.venus.com/services'
            '/ProductService.asmx/GetMoreDetails')
        http_header = {
                "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/535.11 (KHTML, like Gecko) "
                    "Chrome/17.0.963.46 Safari/535.11",
                "Accept" : "text/xml,application/xml,application"
                    "/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,"
                    "text/png,*/*;q=0.5",
                "Accept-Language" : "en-us,en;q=0.5",
                "Accept-Charset" : "ISO-8859-1",
                "Content-type": "application/json; charset=UTF-8",
                }
        idx1 = description_str.find('[{"ID":')
        if idx1 != -1:
            idx2 = description_str.find(',', idx1)
            productID_str = description_str[idx1 + len('[{"ID":'):idx2].strip()
        params = ''.join(["{\"productID\":", productID_str, "}"])
        timeout = 15
        socket.setdefaulttimeout(timeout)
        cookie_jar = cookielib.LWPCookieJar()
        cookie = urllib2.HTTPCookieProcessor(cookie_jar)
        opener = urllib2.build_opener(cookie)
        req = urllib2.Request(more_detail_url, params, http_header)
        res = opener.open(req)
        content = self.__try_read_content(res)

        return content

    def __try_read_content(self, response):
        _count = 0
        content = ''
        while True:
            try:
                content = response.read()
            except :
                log.msg("Error: can\'t read data or IncompleteRead.", log.DEBUG)
                if _count == 3:
                    log.msg("Has tried 3 times. Give up.", log.DEBUG)
                    break
                _count = _count + 1
                continue
            else:
                break
        return content

    def __try_extract_productinfo(self, sel):
        for line in sel.response.body.split('\n'):
            idx1 = line.find('var PageLevelData =')
            if idx1 != -1:
                idx2 = line.find('}]}', idx1)
                __productinfo = \
                    line[idx1 + len('var PageLevelData ='):idx2].strip()
                break
        return __productinfo

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
