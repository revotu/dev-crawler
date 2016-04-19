# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'karmaloop'

class KarmaloopSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["karmaloop.com"]
    is_first = True

    def __init__(self, *args, **kwargs):
        super(KarmaloopSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        if(url.find('#') != -1):
            url = url.replace('.htm#!', '?')
            url = url + '&ajax=true&version=1'
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@id="products-list"]//a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        base_url = ''
        nexts_xpath = '//a[@class="next-page filter-clickable"]/@href'
        nexts = sel.xpath(nexts_xpath).extract()
        if(len(nexts) != 0):
            for path in nexts:
                list_url = path
                if path.find(base_url) == -1:
                    list_url = base_url + path
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
        else:
            if(self.is_first == False):
                return requests
            self.is_first = False
            num_results_xpath = '//span[@class="num-results"]/text()'
            num_results = sel.xpath(num_results_xpath).extract()
            pageNum = int(num_results[0]) / 40
            _extra = int(num_results[0]) % 40
            if(_extra > 0):
                pageNum += 1
            index = 1
            _url = sel.response.url
            while(index < pageNum):
                index += 1
                list_url = _url + '&Page=' + str(index)
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
        item['store_name'] = 'Karmaloop'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//a[@id = "brand"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//p[@class="part-number"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'\n+|\r+|\t+|[()#]|Style')
            _sku = data_re.sub('', data[0]).strip()
            item['sku'] = _sku

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@title="details"]'
        data = sel.xpath(description_xpath).extract()
        _description = ''
        if len(data) != 0:
            _description = data[0]
        item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        _imgs = []
        imgs_url_xpath = '//ul[@class="thumbs noscript"]//a/@data-cloudzoom'
        imgs_url2_xpath = '//ul[@class="thumbs noscript"]//img/@src'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        data_imgs2 = sel.xpath(imgs_url2_xpath).extract()
        if(len(data_imgs) != 0):
            for line in data_imgs:
                idx1 = line.find("zoomImage: '")
                idx2 = line.find("'", idx1 + len("zoomImage: '"))
                _image_url = line[idx1 + len("zoomImage: '"):idx2]
                _imgs.append(_image_url)
        elif(len(data_imgs2) != 0):
            _imgs = data_imgs2
        item['image_urls'] = _imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price1_xpath = '//span[@class="sale-price"]/text()'
        price2_xpath = '//p[@class="price"]/text()'
        data1 = sel.xpath(price1_xpath).extract()
        data2 = sel.xpath(price2_xpath).extract()
        _price = ''
        if len(data1) != 0:
            data_re = re.compile(r'\n+|\t+|\r+|[$]')
            _price = data_re.sub('', data1[0])
        if len(data2) != 0:
            for line in data2:
                if(line.find('$') != -1):
                    data_re = re.compile(r'\n+|\t+|\r+|[ $]')
                    _price = data_re.sub('', line)
                    break
        item['price'] = self._format_price("USD", _price)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//p[@class="overridden"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        _list_price = ''
        if len(data) != 0:
            for line in data:
                if(line.find('$') != -1):
                    data_re = re.compile(r'\n+|\t+|\r+|[ $]')
                    _list_price = data_re.sub('', line)
                    break
            item['list_price'] = self._format_price("USD", _list_price)

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
