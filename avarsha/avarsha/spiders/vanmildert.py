# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re
import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'vanmildert'

class VanmildertSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["vanmildert.com"]
    is_first = True

    def __init__(self, *args, **kwargs):
        super(VanmildertSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx = url.find('#')
        if(idx != -1):
            _url = url[:idx]
            req = urllib2.Request(_url)
            res_data = urllib2.urlopen(req)
            _var1 = ('http://www.vanmildert.com/DesktopModules/BrowseV2/API'
                '/BrowseV2Service/GetProductsInformation?')
            _var2 = ('&isSearch=false&descriptionFilter=&columns=3'
                '&mobileColumns=2&clearFilters=false'
                '&pathName=%2Fwomens%2Fshort-sleeve-tops&searchTermCategory='
                '&selectedCurrency=GBP')
            _body = res_data.read()
            _categoryName = ''
            _currentPage = 1
            _productsPerPage = 24
            _sortOption = 'recent'
            _selectedFilters = ''
            for line in _body.split('\n'):
                idx1 = line.find("'categoryId' : '")
                if(idx1 != -1):
                    idx2 = line.find("' }", idx1)
                    _categoryName = line[idx1 + len("'categoryId' : '"):idx2]
                    break
            idx1 = url.find('&Filter=', idx)
            _selectedFilters = url[idx1 + len('&Filter='):]
            _url = (_var1 + 'categoryName=' + str(_categoryName)
                + '&currentPage=1&productsPerPage=24&sortOption=recent'
                + '&selectedFilters=' + _selectedFilters + _var2)
            url = _url
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        base_url = 'http://www.vanmildert.com'
        _url = sel.response.url
        idx = _url.find('GetProductsInformation')
        if(idx != -1):
            line = sel.response.body
            while(True):
                idx1 = line.find('PrdUrl":"')
                if(idx1 != -1):
                    idx2 = line.find('",', idx1)
                    item_url = base_url + line[idx1 + len('PrdUrl":"'):idx2]
                    item_urls.append(item_url)
                    request = scrapy.Request(item_url, callback=self.parse_item)
                    requests.append(request)
                    line = line[idx2:]
                else:
                    break
        else:
            items_xpath = '//div[@class="s-producttext-top-wrapper"]/a/@href'
            item_nodes = sel.xpath(items_xpath).extract()
            requests = []
            for path in item_nodes:
                item_url = path
                if path.find(base_url) == -1:
                    item_url = base_url + path
                item_urls.append(item_url)
                request = scrapy.Request(item_url, callback=self.parse_item)
                requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        if(self.is_first == False):
            return requests
        self.is_first = False
        total_products_xpath = '//span[@class="pppt"]/span/text()'
        data = sel.xpath(total_products_xpath).extract()
        _total_products = 0
        _total_pages = 0
        _index = 0
        line = sel.response.body
        if(len(data) != 0):
            _total_products = int(data[0])
        else:
            idx1 = line.find('totalProducts":"<span>')
            if(idx1 != -1):
                idx2 = line.find("</span>", idx1)
                _total_products = int(
                    line[idx1 + len('totalProducts":"<span>'):idx2])
        _total_pages = _total_products / 24
        base_url = 'http://www.vanmildert.com'
        list_url = ''
        _url = sel.response.url
        idx = _url.find('GetProductsInformation')
        if(idx != -1):
            list_url = _url
        else:
            nexts_xpath = "//a[@class='swipeNextClick NextLink']/@href"
            nexts = sel.xpath(nexts_xpath).extract()
            if(len(nexts) != 0):
                list_url = nexts[0]
        if list_url.find(base_url) == -1:
            list_url = base_url + list_url
        while(_index < _total_pages):
            _index += 1
            idx = _url.find('GetProductsInformation')
            if(idx != -1):
                idx1 = _url.find('currentPage=')
                if(idx1 != -1):
                    idx2 = _url.find('&', idx1)
                    _var1 = _url[:idx1 + len('currentPage=')]
                    _var2 = _url[idx2:]
                    list_url = _var1 + str(_index + 1) + _var2
            else:
                idx1 = list_url.find('dcp=')
                if(idx1 != -1):
                    idx2 = list_url.find('&', idx1)
                    if(idx2 != -1):
                        list_url = (list_url[:idx1 + len('dcp=')]
                            + str(_index + 1) + list_url[idx2:])
                idx1 = list_url.find('DescriptionFilter=')
                if(idx1 != -1):
                    idx2 = list_url.find('&', idx1)
                    _var1 = list_url[:idx1 + len('DescriptionFilter=')]
                    _var2 = list_url[idx1 + len('DescriptionFilter='):idx2]
                    _var3 = list_url[idx2:]
                    _var2 = (_var2.replace('&', '%26').replace(' ', '%20')
                        .replace('/', '%2F').replace('"', '%22')
                        .replace('[', '%5B').replace(']', '%5D')
                        .replace('{', '%7B').replace('}', '%7D'))
                    list_url = _var1 + _var2 + _var3
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@id="ProductName"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'<[^<>]+>|\n+|\r+|\t+|  +')
            item['title'] = data_re.sub('', data[0]).strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Vanmildert'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = (
            '//li[@class="MoreFromLinksRow"]/a[@href=/brands]/../a[2]/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]
        else:
            item['brand_name'] = 'Vanmildert'

    def _extract_sku(self, sel, item):
        sku_xpath = "//p[@class='productCode']/text()"
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'<[^<>]+>|\n+|\r+|\t+|  +|Product code: ')
            item['sku'] = str(data_re.sub('', data[0]).strip())

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//span[@itemprop="description"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        for line in sel.response.body.split('\n'):
            idx = line.find('colourVariantsInitialData')
            if(idx != -1):
                idx = line.find('AlternateImages')
                if(idx != -1):
                    line = line[idx:]
                while(True):
                    idx1 = line.find('ImgUrlXXLarge":"')
                    if(idx1 != -1):
                        idx2 = line.find('"}', idx1)
                        _img_url = line[idx1 + len('ImgUrlXXLarge":"'):idx2]
                        imgs.append(_img_url)
                        line = line[idx2:]
                    else:
                        break
                item['image_urls'] = imgs
                break

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@id="lblSellingPrice"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(u'<[^<>]+>|\n+|\r+|\t+|  +|["£]')
            new_data = data_re.sub('', data[0])
            item['price'] = self._format_price('GBP', new_data)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@id="lblTicketPrice"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(u'<[^<>]+>|\n+|\r+|\t+|  +|["£]')
            new_data = data_re.sub('', data[0])
            item['list_price'] = self._format_price('GBP', new_data)

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
