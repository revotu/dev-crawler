# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline

import urllib2

from avarsha_spider import AvarshaSpider

from scrapy.selector import Selector


_spider_name = 'dailylook'

class DailylookSpider(AvarshaSpider):
    name = "dailylook"
    allowed_domains = ["dailylook.com"]

    def __init__(self, *args, **kwargs):
        super(DailylookSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        idx1 = sel.response.url.find('size=1000')
        if idx1 == -1:
            idx1 = sel.response.url.find('?')
            if idx1 != -1:
                all_page_url = sel.response.url + '&size=1000'
            else:
                all_page_url = sel.response.url + '?size=1000'
            body = urllib2.urlopen(all_page_url).read()
            sel = Selector(text = body)

        base_url = 'http://www.dailylook.com'
        items_xpath = '//div[@itemprop="name"]/a/@href'
        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Dailylook'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Dailylook'

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@data-product-hook="productID"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = (
            '//div[@class="product_detail_detailsContainer "]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line.strip()
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//div[@data-image-slider-hook="detailContainer"]'
            '/ul//li/img/@data-zoom-image')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//span[@data-product-hook="subcategoryIDName"]/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//div[@data-product-hook="variantSwatch"]/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@itemprop="standardPrice"]/text()'
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