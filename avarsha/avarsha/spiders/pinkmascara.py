# -*- coding: utf-8 -*-
# author: yangxiao


import re

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'pinkmascara'

class PinkmascaraSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["pinkmascara.com"]
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36')

    def convert_url(self, url):
        if '#' in url:
            return url[:url.index('#')]
        if ' ' in url:
            return url.replace(' ', '%20')
        else:
            return url

    def __init__(self, *args, **kwargs):
        super(PinkmascaraSpider, self).__init__(*args, **kwargs)

        setting = get_project_settings()
        setting.set('User-Agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.pinkmascara.com'
        items_xpath = ('//div[@id="productgallery"]/div[@class="product"]'
            '/a[@class="productlink images"]/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.pinkmascara.com'
        nexts_xpath = ('//div[@class="pagecontrol"]/ul[@class="pager"]'
            '/li/a/@href')

        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_urls.append(self.convert_url(list_url))
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@id="content"]/form[@method="post"]/h2/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = re.search('(\S.*)$', data[0]).group(1)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'pinkmascara'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//div[@id="content"]/form/h3[@class="vendor"]'
            '/a/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = re.search('(\S.*)$', data[0]).group(1)

    def _extract_sku(self, sel, item):
        try:
            item['sku'] = re.search('"styleNumber":"(.+?)"', \
                sel.response.body).group(1)
        except:
            item['sku'] = re.search('product_id: ".+_(.+?)"', \
                sel.response.body).group(1)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@id="product-description"]/text() |'
            '//div[@id="product-description"]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath1 = '//a[@id="PrimaryFullsizeLink"]/@href'
        imgs_xpath2 = '//div[@class="thumbnails"]/a/@href'
        data1 = sel.xpath(imgs_xpath1).extract()
        data2 = sel.xpath(imgs_xpath2).extract()
        if len(data1) != 0:
            item['image_urls'] = \
                map(lambda i:'http://www.pinkmascara.com' + i, data1 + data2)

    def _extract_colors(self, sel, item):
        color_xpath = '//ul[@id="colorchoices"]/li/a/@title'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//ul[@id="sizechoices"]/li/a/span/text()'
        size_list = sel.xpath(size_xpath).extract()
        if len(size_list) != 0:
            item['sizes'] = \
                map(lambda i: re.search('(\S.*)$', i).group(1), size_list)

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        try:
            price_number = re.search('"formattedPrice":"\$(.*?)"', \
                sel.response.body).group(1)
            item['price'] = self._format_price("USD", price_number)
        except AttributeError:
            price_xpath = '//div[@id="price"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = re.search('\$(.*)', data[-1]).group(1)
                item['price'] = self._format_price("USD", price_number)

    def _extract_list_price(self, sel, item):
        try:
            price_number = re.search('"formattedOriginalPrice":"\$(.*?)"', \
                sel.response.body).group(1)
            list_price = self._format_price("USD", price_number)
        except AttributeError:
            list_price_xpath = '//div[@id="price"]/span/text()'
            data = sel.xpath(list_price_xpath).extract()
            if len(data) != 0:
                price_number = re.search('\$(.*)', data[0]).group(1)
                list_price = self._format_price("USD", price_number)
        else:
            if list_price != item['price']:
                item['list_price'] = list_price

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

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
