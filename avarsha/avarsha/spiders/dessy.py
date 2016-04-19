# -*- coding: utf-8 -*-
# author: huoda

import gzip
import json
from StringIO import StringIO
import urllib
import urllib2

from scrapy.selector import Selector
import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'dessy'

class DessySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["dessy.com", "s1.dessy.com", "s2.dessy.com",
        "s3.dessy.com", "s4.dessy.com"]

    def __init__(self, *args, **kwargs):
        super(DessySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        url = self.start_urls[0]
        flag = url.find('#')
        if flag == -1:
            base_url = 'http://www.dessy.com'
            items_xpath = '//span[@class="product-name"]/a//@href'
            return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)
        else:
            requests = []
            base_url = 'http://www.dessy.com'
            pageoffset = 2
            key = '{' + url[flag + 1:] + '}'
            while True:
                formdata = {key:''}
                headers = {
                    "Host": "www.dessy.com",
                    "Connection": "keep-alive",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Origin": "http://www.dessy.com",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64)"
                        " AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/42.0.2311.135 Safari/537.36",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.8" }
                post_data = urllib.urlencode(formdata)
                req = urllib2.Request(
                    'http://www.dessy.com/services/genericfilter.ashx?filterty'
                    'pe=ProductFilterProperties&r=0.2901410893537104',
                    post_data, headers)
                response = urllib2.urlopen(req)
                buf = StringIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                text = json.loads(f.read())
                sel_items = Selector(text=text['ContentHtml'])
                f.close()
                item_xpath = '//span[@class="product-name"]/a//@href'
                data = sel_items.xpath(item_xpath).extract()
                if len(data) == 0:
                    break
                else:
                    for url in data:
                        item_url = base_url + url
                        item_urls.append(item_url)
                        requests.append(scrapy.Request(item_url, \
                            callback=self.parse_item))
                    orig = '"ActivePage":' + '%d' % (pageoffset - 1)
                    alt = '"ActivePage":' + '%d' % (pageoffset)
                    pageoffset = pageoffset + 1
                    key = key.replace(orig, alt)
            return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        url = self.start_urls[0]
        flag = url.find('#')
        if flag != -1:
            pass
        else:
            header_xpath = '//form[@name]//@action'
            data = sel.xpath(header_xpath).extract()
            base_url = 'http://www.dessy.com' + data[0]
            flag = base_url.find('?page=')
            if flag != -1:
                base_url = base_url[:flag]
            nexts_xpath = '//div[@class="gutter"][2]//li[@class="num"]//@href'
            return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//title/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0][1:-len(": The Dessy Group ")]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Dessy'

    def _extract_brand_name(self, sel, item):
        flag = sel.response.body.find("'brand': '")
        flag_end = sel.response.body.find("',", flag + 11)
        if (flag != -1) & (flag_end != -1):
            item['brand_name'] = sel.response.body[flag + \
                len("'brand': '"):flag_end]

    def _extract_sku(self, sel, item):
        flag = sel.response.body.find("ecomm_prodid: '")
        flag_end = sel.response.body.find("',", flag + 1)
        if (flag != -1) & (flag_end != -1):
            item['sku'] = sel.response.body[flag + \
                len("ecomm_prodid: '"):flag_end]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        tab_xpath = ('//div[@class="productDescription ' +
            'marginTop20 marginBottom20"]/div/ul//text()')
        data = sel.xpath(tab_xpath).extract()
        count = 0
        found = False
        for tab in data:
            count = count + 1
            if (tab == u'Description') | (tab == u'Details'):
                found = True
                break
        if found:
            description_xpath = ('//div[@class="productDescription marginTop' +
                '20 marginBottom20"]//div[@id="tabs-' + '%d' % count +
                '"]//p/text()')
            data = sel.xpath(description_xpath).extract()
            data = ''.join(data)
            if len(data) != 0:
                item['description'] = data

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//div[@class="imageViews"]/img//@src'
        data = sel.xpath(imgs_xpath).extract()
        for img_url in data:
            img_url = img_url.replace('med', 'yawah')
            imgs.append(img_url)
        if len(imgs) != 0:
            item['image_urls'] = imgs
        else:
            img_xpath = '//img[@id="mainProductImage"]//@src'
            data = sel.xpath(img_xpath).extract()
            if len(data) != 0:
                item['image_urls'] = data


    def _extract_colors(self, sel, item):
        colors_xpath = '//div[@id="primaryColors"]//@data-name'
        data = sel.xpath(colors_xpath).extract()
        item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//option[@value="not-selected"]/../option/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) > 1:
            del data[0]
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@class="details-price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0][1:])
        else:
            # some products such as
            # http://www.dessy.com/dresses/bridesmaid/2931/?colorid=123
            # does not has a price, therefore the price of this kind of product
            # is set 0
            item['price'] = self._format_price('USD', '0')

    def _extract_list_price(self, sel, item):
        pass

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
