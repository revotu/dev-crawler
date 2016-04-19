# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

import math

from avarsha_spider import AvarshaSpider

import urllib2


_spider_name = 'torrid'

class TorridSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["torrid.com"]

    def __init__(self, *args, **kwargs):
        self.header = {'User-Agent' : ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
            '43.0.2357.81 Safari/537.36')}
        super(TorridSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        return url.replace('#', '?')

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        category_url = sel.response.url
        if category_url.find('search') == -1:
            data = sel.xpath('//script/text()').extract()
            for line in data:
                idx1 = line.find('currentFolderId = \'')
                if idx1 == -1:
                    continue
                idx2 = line.find('\'', idx1 + len('currentFolderId = \''))
                folderId = line[idx1 + len('currentFolderId = \''):idx2]
                break
            if len(folderId) == 0:
                return []
            page1_item_url = ('http://www.torrid.com/torrid/trStore/ajax/'
                'getProducts.jsp?sortByFieldId=1&sortByDir=descending&'
                'filterQuery=&folderId=%s&page=1&productsPerPage=100&'
                'userClicked=false' % folderId)
            request = urllib2.Request(page1_item_url)
            response = urllib2.urlopen(request)
            lines = response.read().split('\n')
            idx1 = len(lines) - 1
            maxpage = 1
            while idx1 >= 0:
                if lines[idx1].find('product_count') != -1:
                    idx2 = lines[idx1].find(':')
                    count = int(lines[idx1][idx2 + 1:].strip())
                    maxpage = int(math.ceil(count / (100.0)))
                    break
                idx1 -= 1
            page, requests = 1, []
            while page <= maxpage:
                page_item_url = ('http://www.torrid.com/torrid/trStore/ajax/'
                    'getProducts.jsp?sortByFieldId=1&sortByDir=descending&'
                    'filterQuery=&folderId=%s&page=%d&productsPerPage=100&'
                    'userClicked=false' % (folderId, page))
                request = urllib2.Request(page_item_url)
                response = urllib2.urlopen(request)
                lines = response.read().split('\n')
                idx, maxlen = 0, len(lines) - 1
                while idx <= maxlen:
                    idx1 = lines[idx].find('prodHrefLink\" : \"')
                    if idx1 != -1:
                        idx2 = lines[idx].find('\",', idx1)
                        item_url = 'http://www.torrid.com' + lines[idx][idx1 + \
                                len('prodHrefLink\" : \"'):idx2]
                        item_urls.append(item_url)
                        requests.append(scrapy.Request(item_url, \
                                callback = self.parse_item))
                    idx += 1
                page += 1
            return requests
        else:
            base_url = ''
            items_xpath = '//div[@class="Content"]/a/@href'
            return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        category_url = sel.response.url
        if category_url.find('search') != -1:
            nexts_xpath = (
                '//a[@class="pageselectorlink pageselectornext"]/@href')
            nexts = sel.xpath(nexts_xpath).extract()
            requests = []
            for list_url in nexts:
                list_urls.append(list_url)
                request = scrapy.Request(list_url, headers = self.header, \
                    callback = self.parse)
                requests.append(request)
            return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//li[@class="pTitle"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Torrid'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Torrid'

    def _extract_sku(self, sel, item):
        sku_xpath = '//li[@class="pSku"]/span/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//article[@id="productDesc"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line.replace('\n', '').replace('\r', '')\
                    .replace('\t', '').strip()
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        pre_url = 'http://hottopic.scene7.com/is/image/HotTopic/'
        last_url = ['_hi?wid=1360', '_av1?wid=1360', '_av2?wid=1360']
        imgs = []
        num = sel.response.url
        idx1 = num.rfind('-')
        if idx1 != -1:
            idx2 = num.find('.jsp', idx1)
            if idx2 != -1:
                num = num[idx1 + 1:idx2]
                for part_url in last_url:
                    img_url = pre_url + num + part_url
                    imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//li[@class="pPrice"]/text()'
        price1_xpath = '//li[@class="pPrice"]/span[2]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD ', price_number)
        else:
            data = sel.xpath(price1_xpath).extract()
            if len(data) != 0:
                price_number = data[0][len('$'):].strip()
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//li[@class="pPrice"]/span[1]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['list_price'] = self._format_price('USD', price_number)

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

