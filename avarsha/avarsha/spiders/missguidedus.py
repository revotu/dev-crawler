# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'missguidedus'

class MissguidedSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["missguidedus.com"]

    def __init__(self, *args, **kwargs):
        super(MissguidedSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        if(url.find('#') != -1):
            url = url.replace('#', '?')
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        list_url = ''
        _url = sel.response.url
        idx1 = _url.find('ajax')
        idx2 = _url.find('?')
        if(idx1 == -1 and idx2 != 1):
            _pre_url = ''
            _pre_url_xpath = '//div[@id="layered-nav-endpoint"]/@data-url'
            data = sel.xpath(_pre_url_xpath).extract()
            if len(data) != 0:
                _pre_url = data[0]
            list_url = _pre_url + _url[idx2:]
            item_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        elif(idx1 != -1 and idx2 != 1):
            items_xpath = '//div[@class="details"]//a/@href'
            item_nodes = sel.xpath(items_xpath).extract()
            for item_url in item_nodes:
                item_urls.append(item_url)
                request = scrapy.Request(item_url, callback=self.parse_item)
                requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        _cur_page = 0
        cur_page_xpath = '//li[@class="current"]/text()'
        cur_page = sel.xpath(cur_page_xpath).extract()
        if(len(cur_page) != 0):
            _cur_page = int(cur_page[0])
        pageNum = 2
        list_url = ''
        _url = sel.response.url
        idx1 = _url.find('ajax')
        idx2 = _url.rfind('p=')
        idx3 = _url.find('?')
        if(idx1 == -1):
            _pre_url = ''
            _pre_url_xpath = '//div[@id="layered-nav-endpoint"]/@data-url'
            data = sel.xpath(_pre_url_xpath).extract()
            if len(data) != 0:
                _pre_url = data[0]
            if(idx3 == -1):
                list_url = _pre_url + '?p=' + str(pageNum)
            else:
                idx = _url.find('?')
                list_url = (
                    _pre_url
                    + _url[idx:].replace('!', '%21').replace('/', '%2F')
                    + '&p=' + str(pageNum - 1))
        else:
            if(idx2 != -1):
                page_num = _url[idx2 + 2:]
                if(page_num.isdigit()):
                    pageNum = int(page_num)
                    if((_cur_page != 0 and _cur_page < pageNum) or _cur_page == 0):
                        return requests
                    list_url = _url[:idx2 + 2] + str(pageNum + 1)
                else:
                    list_url = _url + '&p=' + str(pageNum)
            else:
                list_url = _url + '&p=' + str(pageNum)
        list_urls.append(list_url)
        request = scrapy.Request(list_url, callback=self.parse)
        requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="product-title"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Missguidedus'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Missguidedus'

    def _extract_sku(self, sel, item):
        sku_xpath = ('//div[@class="product-title"]//'
            'p[@class="prod_code"]/text()')
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = str(data[0])

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="accordion"]//div'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join([data[0], data[1]])

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//ul[@id="more-views-images"]//li/a/@rel'
        data = sel.xpath(imgs_xpath).extract()
        for img in data:
            idx1 = img.find("largeimage: '")
            if idx1 != -1:
                idx2 = img.find("'", idx1 + len("largeimage: '"))
                img_url = img[idx1 + len("largeimage: '"):idx2].strip()
                imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        _size = []
        for line in sel.response.body.split("\n"):
            idx1 = line.find("MissguidedProduct")
            if(idx1 != -1):
                idx2 = line.find('"Size"')
                if(idx2 != -1):
                    line = line[idx2 + len('"Size"'):]
                idx2 = line.find('"label":"')
                while(idx2 != -1):
                    idx3 = line.find('",', idx2 + len('"label":"'))
                    _size.append(line[idx2 + len('"label":"'):idx3])
                    line = line[idx3:]
                    idx2 = line.find('"label":"')
                break
        if len(_size) != 0:
            item['sizes'] = sorted(_size)

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price1_xpath = '//p[@class="special-price"]/span[@class="price"]/text()'
        price2_xpath = '//span[@class="regular-price"]/\
            span[@class="price"]/text()'
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
        list_price_xpath = '//p[@class="old-price"]/span[@class="price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['list_price'] = self._format_price(
                'USD', data_re.sub('', data[0]).strip())

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
