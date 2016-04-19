# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re
import cookielib
import socket
import urllib
import urllib2

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'americanapparel'

class AmericanapparelSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["americanapparel.net"]

    def __init__(self, *args, **kwargs):
        super(AmericanapparelSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://store.americanapparel.net'
        items_xpath = ('//li[@class="product"]/a/@href|//'
            'div[@class="name"]/a/@href')
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                path = urllib.quote(path.encode('utf-8'))
                item_url = base_url + path
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://store.americanapparel.net/search/'
        nexts_xpath = ('//ul[@class="resetlist  pagination"]//li/a/'
            'span[@class="pagn-next"]/../@href')
        nexts = sel.xpath(nexts_xpath).extract()
        if(len(nexts) != 0 and nexts[0] == '#'):
            return []
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="product-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'American Apparel'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'American Apparel'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="product-style"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = str(data[0].strip())

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//table[@class="longDesc-container"]//table//td'
        data = sel.xpath(description_xpath).extract()
        _description = ''
        if len(data) != 0:
            line = data[0]
            idx1 = line.find('<span style="')
            if(idx1 != -1):
                _description = ''.join([line[:idx1], '</td>'])
            else:
                _description = line
            item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        content = self._get_scrips_content(sel)
        if(len(content) != 0):
            while(True):
                idx1 = content.find('"imgXL":"')
                if(idx1 != -1):
                    idx2 = content.find('"}', idx1 + len('"imgXL":"'))
                    image_url = content[idx1 + len('"imgXL":"'):idx2]
                    imgs.append(image_url)
                    content = content[idx2:]
                else:
                    break
        if(len(imgs) == 0):
            image_urls_xpath = '//a[@id="zoom1"]/@href'
            data = sel.xpath(image_urls_xpath).extract()
            if(len(data[0]) != 0):
                imgs.append(data[0])
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price1_xpath = '//div[@id="skuPriceId"]/span[@class="salePrice"]/text()'
        price2_xpath = '//span[@data-test="test"]/text()'
        price1 = sel.xpath(price1_xpath).extract()
        price2 = sel.xpath(price2_xpath).extract()
        if(len(price1) != 0):
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['price'] = self._format_price(
                'USD', data_re.sub('', price1[0]).strip())
        elif(len(price2) != 0):
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['price'] = self._format_price(
                'USD', data_re.sub('', price2[0]).strip())

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="oldPrice"]/text()'
        list_price = sel.xpath(list_price_xpath).extract()
        if(len(list_price) != 0):
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['list_price'] = self._format_price(
                'USD', data_re.sub('', list_price[0]).strip())

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

    def _get_scrips_content(self, sel):
        request_base_URL = ('http://i.americanapparel.net/services/ATG/'
            'Image.ashx?action=GetMorePhoto&StyleID=')
        product_style_xpath = '//div[@class="product-style"]/text()'
        data = sel.xpath(product_style_xpath).extract()
        if(len(data) != 0):
            _product_style = data[0]
            request_base_URL = ''.join([request_base_URL, _product_style])
        http_header = {
            "User-Agent" :
            ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML,"
                " like Gecko) Chrome/17.0.963.46 Safari/535.11"),
            "Accept" :
            ("text/xml,application/xml,application/xhtml+xml,text/"
                "html;q=0.9,text/plain;q=0.8,text/png,*/*;q=0.5"),
            "Accept-Language" :
            "en-us,en;q=0.5",
            "Accept-Charset" : "ISO-8859-1",
            "Content-type": "application/json; charset=UTF-8",
            }
        params = ''
        timeout = 15
        socket.setdefaulttimeout(timeout)
        cookie_jar = cookielib.LWPCookieJar()
        cookie = urllib2.HTTPCookieProcessor(cookie_jar)
        opener = urllib2.build_opener(cookie)
        req = urllib2.Request(request_base_URL, params, http_header)
        res = opener.open(req)

        return self.__try_read_content(res)

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
        return self._remove_escape(content)

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
