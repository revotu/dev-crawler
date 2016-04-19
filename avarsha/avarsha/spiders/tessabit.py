# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re, urllib2, json

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'tessabit'

class TessabitSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["tessabit.com"]
    is_first = True

    def __init__(self, *args, **kwargs):
        super(TessabitSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx = url.find('#')
        if(idx != -1):
            url = url.replace('#', '??')
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        if(self.is_first == False):
            return requests
        self.is_first = False
        base_url = 'http://shop.tessabit.com/'
        _url = sel.response.url.replace('??', '#')
        has_pageNum = False
        idx1 = _url.find('ps=')
        if(idx1 != -1):
            idx2 = _url.find('&', idx1)
            if(idx2 != -1):
                has_pageNum = True
        data_src = self._extract_payload_json(list_url=_url, pageNum=1)
        data = json.loads(data_src)
        if(len(data["d"]["Paging"]["PagingContent"][0]["PagingSelector"]) != 0):
            for i in data["d"]["Paging"]["PagingContent"][0]["PagingSelector"]:
                new_pageNum = i["PagingItemVal"]
                if(has_pageNum == True):
                    _url = (_url[:idx1 + len('ps=')]
                        + str(new_pageNum) + _url[idx2:])
                data_src = (self._extract_payload_json(
                    list_url=_url, pageNum=new_pageNum))
                data = json.loads(data_src)
                for i in data["d"]["Items"]:
                    item_url = i["ItemURL"]
                    if item_url.find(base_url) == -1:
                        item_url = base_url + item_url
                    item_urls.append(item_url)
                    request = scrapy.Request(item_url, callback=self.parse_item)
                    requests.append(request)
        else:
            for i in data["d"]["Items"]:
                item_url = i["ItemURL"]
                if item_url.find(base_url) == -1:
                    item_url = base_url + item_url
                item_urls.append(item_url)
                request = scrapy.Request(item_url, callback=self.parse_item)
                requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="product_Title"]//text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data).strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Tessabit'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//div[@class="product_Title"]/h1/span/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]
        else:
            item['brand_name'] = 'Tessabit'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="mc_sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = str(data[0])

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//span[@id='
            '"ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_lbItDesc"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        image_urls_xpath = '//div[@class="dvtScroll"]//img/@src'
        data = sel.xpath(image_urls_xpath).extract()
        if len(data) != 0:
            for line in data:
                if(line.find('http:') == -1):
                    line = 'http:' + line
                _image_url = line.replace('_70.jpg', '_1000.jpg')
                imgs.append(_image_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = (
            '//span[@class="dvtPriceLoaderRef"]/strike/../span[1]/text()')
        price2_xpath = '//span[@class="dvtPriceLoaderRef"]/text()'
        data = sel.xpath(price_xpath).extract()
        data2 = sel.xpath(price2_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(u'<[^<>]+>|\n+|\r+|\t+|[ $€]|,00')
            new_data = data_re.sub('', data[0])
            if(data[0].find(u'€') != -1):
                item['price'] = self._format_price('EUR', new_data)
            elif(data[0].find(u'$') != -1):
                item['price'] = self._format_price('USD', new_data)
        elif len(data2) != 0:
            data_re = re.compile(u'<[^<>]+>|\n+|\r+|\t+|[ $€]|,00')
            new_data = data_re.sub('', data2[0])
            if(data2[0].find(u'€') != -1):
                item['price'] = self._format_price('EUR', new_data)
            elif(data2[0].find(u'$') != -1):
                item['price'] = self._format_price('USD', new_data)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//span[@class="dvtPriceLoaderRef"]/strike/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(u'<[^<>]+>|\n+|\r+|\t+|[ $€]|,00')
            new_data = data_re.sub('', data[0])
            if(data[0].find(u'€') != -1):
                item['list_price'] = self._format_price('EUR', new_data)
            elif(data[0].find(u'$') != -1):
                item['list_price'] = self._format_price('USD', new_data)

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

    def _extract_payload_json(self, list_url, pageNum):
        _url = 'http://shop.tessabit.com/FFAPI/MultiSelect.asmx/GetDataItems'
        headers = {
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Cache-Control':'no-cache',
            'Content-Type':'application/json; charset=UTF-8',
            'Host':'shop.tessabit.com',
            'Origin':'http://shop.tessabit.com',
            'Pragma':'no-cache',
            'Proxy-Connection':'keep-alive',
            'Referer':('http://shop.tessabit.com'
                '/shopping/women/clothing-1/items.aspx'),
            'X-Requested-With':'XMLHttpRequest'
        }
        payload = {
            'URL': '',
            'QueryString': 'ps=1&pv=60',
            'IDFilterCaller': '0',
            'DeepFilterCaller': '0',
            'ValFilterCaller': '0',
            'PagingSelector': '1',
            'PagingView': '60',
            'OrderBy': '0',
            'OnlyItems': 'false'
        }
        idx = list_url.find('#')
        if(idx != -1):
            payload['QueryString'] = list_url[idx + len('#'):]
        payload['URL'] = list_url
        payload['PagingSelector'] = str(pageNum)
        req = urllib2.Request(
            url=_url, data=json.dumps(payload), headers=headers)
        res = urllib2.urlopen(req)
        body = res.read()
        res.close
        return body

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
