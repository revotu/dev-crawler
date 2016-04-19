# -*- coding: utf-8 -*-
# author: huoda

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'tillys'

class TillysSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["tillys.com"]

    def __init__(self, *args, **kwargs):
        super(TillysSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        flag = sel.response.url.find('N-')
        flag += 2
        N = sel.response.url[flag:]
        No = 0
        source_url1 = ('http://www.tillys.com/tillys/cartridges/'
            'ResultsList/resultListCategoryFrag.jsp?No=')
        source_url2 = '&N=' + N
        source_url = source_url1 + str(No) + source_url2
        response = urllib2.urlopen(source_url).read()
        sel_items = Selector(text=response)
        base_url = 'http://www.tillys.com'
        item_xpath = '//div[@class="prd-name"]/a//@href'
        data = sel_items.xpath(item_xpath).extract()
        while len(data) != 0:
            for url in data:
                item_url = base_url + url
                item_urls.append(item_url)
                requests.append(scrapy.Request(item_url, \
                    callback=self.parse_item))
            No += 24
            source_url = source_url1 + str(No) + source_url2
            response = urllib2.urlopen(source_url).read()
            sel_items = Selector(text=response)
            data = sel_items.xpath(item_xpath).extract()
        if len(data) == 0:
            item_xpath = '//div[@itemprop="itemListElement"]/a//@href'
            data = sel.xpath(item_xpath).extract()
            for url in data:
                item_url = base_url + url
                item_urls.append(item_url)
                requests.append(scrapy.Request(item_url, \
                    callback=self.parse_item))
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@id="pdpNameContainer"]/span//text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Tillys'

    def _extract_brand_name(self, sel, item):
        brand_xpath = ('//div[@id="brandContainer"]//'
            'span[@itemprop="brand"]//text()')
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0 :
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@id="itemNumber"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="collapsible-container-content'
            ' collapsed"]/text()')
        data = sel.xpath(description_xpath).extract()
        des = ''
        for line in data:
            line = line.strip()
            if len(line) > 10:
                des = des + line
        if len(des) != 0:
            item['description'] = des

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_urls = []
        img1_xpath = '//div[@class="item active"]/img//@src'
        data = sel.xpath(img1_xpath).extract()
        if len(data) != 0:
            img_urls.append(data[0])
        img_xpath = '//div[@class="item"]/img//@xsrc'
        data = sel.xpath(img_xpath).extract()
        for img in data:
            if len(img) != 0:
                img_urls.append(img)
        if len(img_urls) != 0:
            item['image_urls'] = img_urls

    def _extract_colors(self, sel, item):
        flag = sel.response.body.find('var product = {')
        flag_end = sel.response.body.find('var pm =', flag)
        global text
        text = sel.response.body[flag:flag_end].strip()
        colors = []
        flag = text.find('colorDescription')
        while flag != -1:
            flag_end = text.find('","', flag + 1)
            color = text[flag + len('colorDescription":"'):flag_end]
            if color in colors:
                pass
            else:
                colors.append(color)
            flag = text.find('colorDescription', flag_end + 1)
        item['colors'] = colors

    def _extract_sizes(self, sel, item):
        sizes = {}
        number = len(item['colors'])
        flag = text.find('"size":"')
        while flag != -1:
            flag_end = text.find('","', flag + 1)
            size = text[flag + len('"size":"'):flag_end]
            sizes[size] = sizes.get(size, 0) + 1
            flag = text.find('"size":"', flag_end + 1)
        size_temp = []
        for size in sizes.keys():
            if sizes[size] == number:
                size_temp.append(size)
        if len(size_temp) != 0:
            item['sizes'] = size_temp

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        flag = text.find('"nowPrice":"')
        if flag == -1:
            item['price'] = self._format_price('USD', '0')
        else:
            flag_end = text.find('","', flag + 1)
            price_temp = text[flag + len('"nowPrice":"'):flag_end]
            flag = price_temp.find('-')
            if flag == -1:
                item['price'] = self._format_price('USD', price_temp)
            else:
                low_price = price_temp[:flag - 1]
                high_price = price_temp[flag + 1:]
                item['low_price'] = self._format_price('USD', low_price)
                item['price'] = item['low_price']
                item['high_price'] = self._format_price('USD', high_price)

    def _extract_list_price(self, sel, item):
        flag = text.find('wasPrice":"')
        if flag != -1:
            flag_end = text.find('","', flag + 1)
            list_price = text[flag + len('wasPrice":"'):flag_end]
            item['list_price'] = self._format_price('USD', list_price)

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
