# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'runway2street'

class Runway2streetSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["runway2street.com"]

    def __init__(self, *args, **kwargs):
        super(Runway2streetSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        return url.replace('[]', '%5B%5D').replace(' ', '%20')

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@class="box-caption grid-info"]/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'https://www.runway2street.com'
        nexts_xpath = '//li[@class="pagernext"]/a/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h2[@class="designer-subtitle no-bottom"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'r2s'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//h1[@class='
            '"designer-title top-margin no-bottom"]/a/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = ('//input[@id="ProductID"]/@value')
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = str(data[0].strip())

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="accordion"]/article'
        data = sel.xpath(description_xpath).extract()
        _description = ''
        if len(data) != 0:
            _description = ''.join([_description, data[0]])
        item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_url_xpath = ('//div[@class="slideshow-wrapper"]'
            '//li/a[@class="swipebox"]/@href')
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        if(len(data_imgs) != 0):
            item['image_urls'] = data_imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price1_xpath = ('//h5[@itemprop="offers"]/span[@style='
            '"font-weight: bold"]/text()')
        price2_xpath = "//meta[@itemprop='price']/@content"
        price1 = sel.xpath(price1_xpath).extract()
        price2 = sel.xpath(price2_xpath).extract()
        if(len(price1) != 0):
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['price'] = self._format_price(
                'USD', data_re.sub('', price1[0]).strip())
        elif(len(price2) != 0):
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['price'] = self._format_price(
                'USD', data_re.sub('', price2[0]).strip())

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="large-6 columns"]//span[@style='
            '"text-decoration: line-through"]/text()')
        list_price = sel.xpath(list_price_xpath).extract()
        if(len(list_price) != 0):
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['list_price'] = self._format_price(
                'USD', data_re.sub('', list_price[0]).strip())

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
