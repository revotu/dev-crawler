# -*- coding: utf-8 -*-
# author: huoda

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'michaelkors'

class MichaelkorsSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["michaelkors.com"]

    def __init__(self, *args, **kwargs):
        super(MichaelkorsSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        base_url = ('http://www.michaelkors.com/' +
            'browse/search/lazyLoading.jsp?No=')
        self_url = sel.response.url
        flag = self_url.rfind('/')
        end_url = self_url[flag + 1:]
        end_url = end_url.replace('-', '=')
        No = 0
        source_url = base_url + '%d' % No + '&' + end_url
        page = urllib2.urlopen(source_url)
        if page:
            page = page.read()
            self_sel = Selector(text=page)
        item_xpath = '//div[@class="product_panel"]/a//@href'
        data = self_sel.xpath(item_xpath).extract()
        while len(data) != 0:
            url1 = 'http://www.michaelkors.com'
            for url in data:
                item_url = url1 + url
                item_urls.append(item_url)
                requests.append(scrapy.Request(\
                    item_url, callback=self.parse_item))
            No = No + 99
            source_url = base_url + '%d' % No + '&' + end_url
            page = urllib2.urlopen(source_url)
            if page:
                page = page.read()
                self_sel = Selector(text=page)
            data = self_sel.xpath(item_xpath).extract()
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url
        item['url'] = item['url'].replace('%C3%A9', '\xe9')

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="inner_container"]' +
            '//*[@class="prod_name"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Michael Kors'

    def _extract_brand_name(self, sel, item):
        brand_xpath = ('//div[@class="inner_container"]' +
            '//*[@class="brand_name"]/text()')
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = ('//div[@class="inner_container"]' +
            '//*[@id="store_number"]/text()')
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data = data[0][len('Store Style #: '):]
            item['sku'] = data

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        des = ''
        description1_xpath = ('//div[@class="pdp_description_content ' +
            'jspScrollable pdp_description_tabs_1"]/p')
        data = sel.xpath(description1_xpath).extract()
        if len(data) != 0:
            des = des + data[0]
        description2_xpath = ('//div[@class="pdp_description_content ' +
            'jspScrollable pdp_description_tabs_2"]/ul')
        data = sel.xpath(description2_xpath).extract()
        if len(data) != 0:
            des = des + data[0]
        if len(des) != 0:
            item['description'] = des

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_urls = []
        img_xpath = '//div[@id="imageSetPath"]/text()'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            data = data[0][len('MichaelKors/'):]
            url1 = 'http://michaelkors.scene7.com/is/image//MichaelKors/'
            url2 = '?req=set'
            url = url1 + data + url2
            page = urllib2.urlopen(url).read()
            self_sel = Selector(text=page)
            img_xpath2 = '//item/i//@n'
            data = self_sel.xpath(img_xpath2).extract()
            base_url = 'http://michaelkors.scene7.com/is/image/'
            end_url = ('?$ProductMain$&id=VPFRZ0&scl=3&' +
                'req=tile&rect=0,0,1000,1000&fmt=jpg')
            for url in data:
                img_url = base_url + url + end_url
                img_urls.append(img_url)
            if len(img_urls) != 0:
                item['image_urls'] = img_urls

    def _extract_colors(self, sel, item):
        colors = []
        colors_xpath = '//ul[@class="color_group_list color_swatch"]//@onclick'
        data = sel.xpath(colors_xpath).extract()
        if len(data) != 0:
            for col in data:
                flag = col.find('colorChangeOmni')
                if flag != -1:
                    flag_end = col.find("','", flag + 1)
                    color = col[flag + len("colorChangeOmni('"):flag_end]
                    colors.append(color)
        if len(colors) != 0:
            item['colors'] = colors

    def _extract_sizes(self, sel, item):
        size_xpath = '//select[@class="size_select"]/option/text()'
        data = sel.xpath(size_xpath).extract()
        sizes = []
        for size in data:
            size = size.strip()
            if (size.find('CHOOSE') == -1) & (size.find('Sold Out') == -1):
                sizes.append(size)
        if len(sizes) != 0:
            item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@id="productPrice"]//input//@value'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[-1] + '0')

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@id="productPrice"]/' +
            'span[@class="strike_price"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            price_number = price_number[1:]
            item['list_price'] = self._format_price('USD', price_number)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        item['is_free_shipping'] = True


def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
