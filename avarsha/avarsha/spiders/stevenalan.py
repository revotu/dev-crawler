# -*- coding: utf-8 -*-
# author: huoda

import string
import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'stevenalan'

class StevenalanSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ['stevenalan.com']

    def __init__(self, *args, **kwargs):
        super(StevenalanSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        flag = url.find('#')
        if flag == -1:
            return url
        else:
            url = url[flag + 1:]
            return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.stevenalan.com'
        items_xpath = '//div[@class="overlay fade"]/a//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.stevenalan.com'
        nexts_xpath = '//a[@class="pagenext" and @href]//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="productname"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data = data[0].strip()
        if len(data) != 0:
            item['title'] = data

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Steven Alan'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@class="productbrand"]/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            data = data[0].strip()
        if len(data) != 0:
            item['brand_name'] = data

    def _extract_sku(self, sel, item):
        sku_xpath = '//*//@data-id'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data = data[0].strip()
        if len(data) != 0:
            item['sku'] = data

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="product_details"]/p/text()'
        data = sel.xpath(description_xpath).extract()
        description = '<br>'.join(data)
        if len(description) != 0:
            item['description'] = description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_urls = []
        pressid_path = '//meta[@property="og:image" and @ content]/@content'
        data = sel.xpath(pressid_path).extract()
        if len(data) != 0:
            flag = data[0].find('StevenAlan/')
            pressid = data[0][flag + len('StevenAlan/'):]
            pressid = pressid.replace('_PD', '_IS')
            pressid = pressid.replace('_OB', '_IS')
        if len(pressid) != 0:
            url1 = 'http://s7d9.scene7.com/is/image/StevenAlan/'
            url2 = '?$pdplarge$&req=imageset'
            url = url1 + pressid + url2
            sourcepage = urllib2.urlopen(url).read()
        if len(sourcepage) != 0:
            group = sourcepage.split(';')
            urls = []
            for i in group:
                t = i.split(',')
                urls = urls + t
            urls = list(set(urls))
        base_url = 'http://s7d9.scene7.com/is/image/'
        end_url = '?$fullSizeZoom$'
        for url in urls:
            url = url.strip()
            url = base_url + url + end_url
            img_urls.append(url)
        if len(img_urls) != 0:
            item['image_urls'] = img_urls

    def _extract_colors(self, sel, item):
        color_xpath = '//div[@class="swatches color"]//a/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size = []
        size_xpath = ('//div[@class="swatches size"]//' +
            'ul[@class="swatchesdisplay"]//text()')
        data = sel.xpath(size_xpath).extract()
        for s in data:
            s = s.strip()
            if len(s) != 0:
                size.append(s)
        if len(size) != 0:
            item['sizes'] = size

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="salesprice"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            data = data[0]
            item['price'] = self._format_price('USD', data[1:])
        else:
            price_xpath = '//div[@class="salesprice itemOnSale"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                data = data[0]
                item['price'] = self._format_price('USD', data[1:])

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="standardprice"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data = data[0]
            item['list_price'] = self._format_price('USD', data[1:])

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        if len(item['price']) > 5:
            price = item['price'][4:]
            price = string.atof(price)
            if price > 150:
                item['is_free_shipping'] = True
            else:
                item['is_free_shipping'] = False


def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
