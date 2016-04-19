# -*- coding: utf-8 -*-
# author: huoda

import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'theclutcher'

class TheclutcherSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["theclutcher.com"]

    def __init__(self, *args, **kwargs):
        super(TheclutcherSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.theclutcher.com'
        items_xpath = '//li[@class="product"]/p/a//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = sel.response.url
        flag = base_url.find('?')
        if flag != -1:
            base_url = base_url[:flag]
        nexts_xpath = '//li[@class="next"]/a//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        requests = []
        nexts = sel.xpath(nexts_xpath).extract()
        if len(nexts) != 0:
            for path in nexts:
                list_url = path
                if path.find(base_url) == -1:
                    list_url = base_url + path
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
            return requests
        else:
            page = 2
            list_url = self.start_urls[0] + '&currPage=' + str(page)
            nex = urllib2.urlopen(list_url).read()
            while 'class="product"' in nex:
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
                page += 1
                list_url = self.start_urls[0] + '&currPage=' + str(page)
                nex = urllib2.urlopen(list_url).read()
            return requests


    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="product-detail stage"]'
            '//h3[@itemprop="name"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'theclutcher'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@class="product-detail stage"]//h1//text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        flag = sel.response.url.find('product/')
        if flag != -1:
            item['sku'] = sel.response.url[flag + 8:]

    def _extract_price(self, sel, item):
#         print sel.response.body
        price_xpath = ('//div[@class="price-box"]//span[@class="promo" '
            'and @itemprop="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][2:].strip()
            flag1 = price_number.find(',')
            flag2 = price_number.find('.')
            if (flag1 != -1) & (flag2 == -1):
                price_number = price_number.replace(',', '.')
            elif (flag2 != -1) & (flag2 < flag1):
                price_number = price_number.replace('.', ',')
                flag = price_number.rfind(',', 0, -1)
                price_number = price_number[:flag] + '.' \
                    + price_number[flag + 1:]
            if data[0].find('\u20ac') != 0:
                item['price'] = self._format_price('GBP', price_number)
            else:
                item['price'] = self._format_price('USD', price_number)
        else:
            item['price'] = self._format_price('GBP', '0')

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="price-box"]//'
            'span[@class="strike"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][2:].strip()
            flag1 = price_number.find(',')
            flag2 = price_number.find('.')
            if (flag1 != -1) & (flag2 == -1):
                price_number = price_number.replace(',', '.')
            elif (flag2 != -1) & (flag2 < flag1):
                price_number = price_number.replace('.', ',')
                flag = price_number.rfind(',', 0, -1)
                price_number = price_number[:flag] + '.' \
                    + price_number[flag + 1:]
            if data[0].find('\u20ac') != 0:
                item['list_price'] = self._format_price('GBP', price_number)
            else:
                item['list_price'] = self._format_price('USD', price_number)

    def _extract_colors(self, sel, item):
        color_xpath = '//select[@class="colors"]//text()'
        data = sel.xpath(color_xpath).extract()
        colors = []
        for color in data:
            color = color.strip()
            if len(color) > 2:
                colors.append(color)
        if len(colors) != 0:
            item['colors'] = colors

    def _extract_sizes(self, sel, item):
        size_xpath = ('//select[@id="idTaglia" and @name="idTaglia" '
            'and @class="sizes"]//text()')
        data = sel.xpath(size_xpath).extract()
        sizes = []
        for size in data:
            size = size.strip()
            if len(size) > 0:
                sizes.append(size)
        if len(sizes) != 0:
            item['sizes'] = sizes

    def _extract_image_urls(self, sel, item):
        image_xpath = '//div[@class="photo-big"]/a//@href'
        data = sel.xpath(image_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="acc-content curr"]/p[1]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
