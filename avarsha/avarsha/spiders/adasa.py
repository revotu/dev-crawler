# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'adasa'

class AdasaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["adasa.com"]

    def __init__(self, *args, **kwargs):
        super(AdasaSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.adasa.com/'
        items_xpath = '//span[@class="prodd"]/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.adasa.com/'
        nexts_xpath = '//p[@class="right"]/a/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="productName"]/text()'
        data = sel.xpath(title_xpath).extract()
        _title = ''
        if len(data) != 0:
            for line in data:
                data_re = re.compile(r'(?:<[^<>]>)+|\n+|\r+|\t+')
                _title = ''.join([_title, data_re.sub('', line)]).strip()
            item['title'] = _title

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'ADASA'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'ADASA'

    def _extract_sku(self, sel, item):
        sku_xpath = '//input[@id="pID"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = str(data[0])

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="productDropDown productDetails"]//ul'
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
        imgs = []
        imgs_url_xpath = '//div[@id="productMainImages"]//img/@src'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        if(len(data_imgs) != 0):
            for line in data_imgs:
                imgs.append('http:' + line)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = \
            '//span[@class="thePrice"]/span[@class="salePrice"]/text()'
        price2_xpath = '//span[@class="thePrice"]/text()'
        price = sel.xpath(price_xpath).extract()
        price2 = sel.xpath(price2_xpath).extract()
        _price = ''
        if(len(price) != 0):
            for line in price:
                if(line.find('$') != -1):
                    data_re = re.compile(
                        r'(?:<[^<>]*>)+|\n+|\r+|\t+| +|[$]|(?:\([^\(\)]*\))+')
                    _price = data_re.sub('', line).strip()
                    break
            item['price'] = self._format_price('USD', _price)
        elif(len(price2) != 0):
            for line in price2:
                if(line.find('$') != -1):
                    data_re = re.compile(r'(?:<[^<>]>)+|\n+|\r+|\t+| +|[$]')
                    _price = data_re.sub('', line).strip()
                    break
            item['price'] = self._format_price('USD', _price)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="thePrice"]/strike/text()'
        list_price = sel.xpath(list_price_xpath).extract()
        _list_price = ''
        if(len(list_price) != 0):
            for line in list_price:
                if(line.find('$') != -1):
                    data_re = re.compile(r'(?:<[^<>]*>)+|\n+|\r+|\t+| +|[$]')
                    _list_price = data_re.sub('', line).strip()
                    break
            item['list_price'] = self._format_price('USD', _list_price)

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
