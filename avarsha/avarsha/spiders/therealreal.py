# -*- coding: utf-8 -*-
# author: wanghaiyi

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = "therealreal"

class TherealrealSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["therealreal.com"]

    def __init__(self, *args, **kwargs):
        super(TherealrealSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.therealreal.com'
        items_xpath = ('//div[@class="search-results"]/'
            'div[@class="product"]/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//a[@rel="next"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@id="product-description"]'
            '/h1[@class="heading h-ml"]')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
            item['title'] = data_re.sub('', data[0])

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Therealreal'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//h1[@itemprop="name"]/a/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@itemprop="sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desp = ''
        description_xpath = ('//div[@class="trr-tab-sections style-1"]//'
            'span[@itemprop="description"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
            data[0] = data_re.sub('', data[0])
            desp += data[0]
        description_xpath = '//div[@data-trr-tab-section="details"]/div'
        data = sel.xpath(description_xpath).extract()
        for per in data:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
            per = data_re.sub('', per)
            desp += per
        item['description'] = desp

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//div[@class="product-thumbnail"]/a/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for img in data:
                img = img.replace('thumbnail', 'enlarged')
                img = 'https:' + img
                imgs.append(img)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@itemprop="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0][len('$'):])

    def _extract_list_price(self, sel, item):
        pass

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