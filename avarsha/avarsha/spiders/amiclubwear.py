# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'amiclubwear'

class AmiclubwearSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["amiclubwear.com"]

    def __init__(self, *args, **kwargs):
        super(AmiclubwearSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//*[@id="nav-and-prodgrid"]/ul//li/h2/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        list_url = ''
        base_url = sel.response.url
        idx1 = base_url.find('?')
        idx2 = base_url.find('p=')
        if(idx2 != -1):
            pageNum = int(base_url[idx2 + len('p='):])
        else:
            pageNum = 1
        cur_page_xpath = '//div[@class="pages"]//li[@class="current"]/text()'
        cur_page = sel.xpath(cur_page_xpath).extract()
        if(len(cur_page) != 0):
            if(pageNum <= int(cur_page[0])):
                if(idx1 != -1):
                    if(idx2 != -1):
                        list_url = base_url[:idx2] + 'p=' + str(pageNum + 1)
                    else:
                        list_url = base_url + '&p=' + str(pageNum + 1)
                else:
                    list_url = base_url + '?p=' + str(pageNum + 1)
        list_urls.append(list_url)
        request = scrapy.Request(list_url, callback=self.parse)
        requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="product-name"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Amiclubwear'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//span[@itemprop="brand"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()
        else:
            item['brand_name'] = 'Amiclubwear'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="style"]/span[@itemprop="sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = str(data[0])

    def _extract_features(self, sel, item):
        pass

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
        imgs_xpath = '//div[@class="more-views"]//li/a/@href'
        data = sel.xpath(imgs_xpath).extract()
        if(len(data) != 0):
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size = []
        size_str = ''
        for line in sel.response.body.split('\n'):
            idx1 = line.find('"options":[')
            if idx1 != -1:
                idx2 = line.find(']}},', idx1)
                size_str = line[idx1 + len('"options":['):idx2].strip()
                break
        while(True):
            idx1 = size_str.find('"label":"')
            if idx1 != -1:
                idx2 = size_str.find('",', idx1)
                size_option = size_str[idx1 + len('"label":"'):idx2].strip()
                size.append(size_option)
                size_str = size_str[idx2:]
            else:
                break
        item['sizes'] = sorted(size)

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="pricecontainer"]'
            '//div[@class="special-price"]//span[@class="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        data_list_price, data_high_price, data_low_price = \
            self._preprocess_list_high_price(sel)
        if len(data_low_price) != 0:
            data_re = re.compile(r'(?:<[^<>]+>)+|\n+|\t+|\r+|[ $*]')
            _price = data_re.sub('', data_low_price[0]).strip()
            item['price'] = self._format_price('USD', _price)
        elif len(data_high_price) != 0:
            data_re = re.compile(r'(?:<[^<>]+>)+|\n+|\t+|\r+|[ $*]')
            _high_price = data_re.sub('', data_high_price[0]).strip()
            item['price'] = self._format_price('USD', _high_price)
        elif(len(data) != 0):
            data_re = re.compile(r'(?:<[^<>]+>)+|\n+|\t+|\r+|[ $*]')
            _price = data_re.sub('', data[0]).strip()
            item['price'] = self._format_price('USD', _price)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="pricecontainer"]'
            '//div[@class="old-price"]//span[@class="price"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        data_list_price, data_high_price, data_low_price = \
            self._preprocess_list_high_price(sel)
        if len(data_high_price) != 0 and len(data_list_price) != 0:
            data_re = re.compile(r'(?:<[^<>]+>)+|\n+|\t+|\r+|[ $*]')
            _list_price = data_re.sub('', data_list_price[0]).strip()
            item['list_price'] = self._format_price('USD', _list_price)
        elif len(data_high_price) != 0 and len(data_low_price) != 0:
            data_re = re.compile(r'(?:<[^<>]+>)+|\n+|\t+|\r+|[ $*]')
            _high_price = data_re.sub('', data_high_price[0]).strip()
            item['list_price'] = self._format_price('USD', _high_price)
        elif(len(data) != 0):
            data_re = re.compile(r'(?:<[^<>]+>)+|\n+|\t+|\r+|[ $*]')
            _list_price = data_re.sub('', data[0]).strip()
            item['list_price'] = self._format_price('USD', _list_price)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        data_list_price, data_high_price, data_low_price = \
            self._preprocess_list_high_price(sel)
        if len(data_high_price) != 0 and len(data_list_price) != 0:
            data_re = re.compile(r'(?:<[^<>]+>)+|\n+|\t+|\r+|[ $*]')
            _high_price = data_re.sub('', data_high_price[0]).strip()
            item['high_price'] = self._format_price('USD', _high_price)

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

    def _preprocess_list_high_price(self, sel):
        list_price_xpath = ('//div[@class="pricecontainer"]//div[@class='
            '"special-price old-price old-price-small"]/span[@class="price"]')
        high_price_xpath = ('//div[@class="pricecontainer"]//'
            'span[@itemprop="highPrice"]')
        price_xpath = ('//div[@class="pricecontainer"]//'
            'span[@itemprop="lowPrice"]')
        data_list_price = sel.xpath(list_price_xpath).extract()
        data_high_price = sel.xpath(high_price_xpath).extract()
        data_low_price = sel.xpath(price_xpath).extract()
        return data_list_price, data_high_price, data_low_price

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
