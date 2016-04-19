# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'profilefashion'

class ProfilefashionSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["profilefashion.com"]

    def __init__(self, *args, **kwargs):
        super(ProfilefashionSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//ul[@class="products-grid clearfix"]//li/a/@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//a[@class="next i-next"]/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'<[^<>]+>|\n+|\r+|\t+|  +')
            item['title'] = data_re.sub('', data[0]).strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Profilefashion'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//span[@itemprop="brand"]/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]
        else:
            item['brand_name'] = 'Profilefashion'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@itemprop="description"]'
        sku2_xpath = '//span[@class="product_id"]/text()'
        data = sel.xpath(sku_xpath).extract()
        data2 = sel.xpath(sku2_xpath).extract()
        _sku = ''
        if len(data) != 0:
            line = data[0]
            idx1 = line.find('Product code: ')
            if(idx1 != -1):
                idx2 = line.find('</', idx1)
                if(idx2 != -1):
                    _sku = line[idx1 + len('Product code: '):idx2]
                    data_re = re.compile(u'<[^<>]+>|\n+|\r+|\t+|  +')
                    _sku = data_re.sub('', _sku)
        if len(_sku) == 0:
            if(len(data2) != 0):
                _sku = data2[0]
        if len(_sku) == 0:
            for line in sel.response.body.split('\n'):
                idx1 = line.find('OptionsPrice({"productId":"')
                if(idx1 != -1):
                    idx2 = line.find('",', idx1)
                    if(idx2 != -1):
                        _sku = (line[idx1 + len('OptionsPrice({"productId":"')
                            :idx2])
                        break
        if len(_sku) != 0:
            item['sku'] = str(_sku)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@itemprop="description"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        image_urls_xpath = ('//div[@class="more-views"]//li/a/@href')
        image_urls2_xpath = (
            '//p[@class="product-image product-img-box"]/a/@href')
        data = sel.xpath(image_urls_xpath).extract()
        data2 = sel.xpath(image_urls2_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data
        elif len(data2) != 0:
            item['image_urls'] = data2

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = (
            '//div[@itemprop="offerDetails"]'
            '//span[@itemprop="price"]/span/text()')
        price2_xpath = ('//div[@itemprop="offerDetails"]'
            '//p[@class="special-price"]//span[@class="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        data2 = sel.xpath(price2_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(u'<[^<>]+>|\n+|\r+|\t+|  +|["£$]')
            new_data = data_re.sub('', data[0])
            if(data[0].find(u'£') != -1):
                item['price'] = self._format_price('GBP', new_data)
            elif(data[0].find('$') != -1):
                item['price'] = self._format_price('USD', new_data)
        elif(len(data2) != 0):
            data_re = re.compile(u'<[^<>]+>|\n+|\r+|\t+|  +|["£$]')
            new_data = data_re.sub('', data2[0])
            if(data2[0].find(u'£') != -1):
                item['price'] = self._format_price('GBP', new_data)
            elif(data2[0].find('$') != -1):
                item['price'] = self._format_price('USD', new_data)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@itemprop="offerDetails"]'
            '//p[@class="old-price"]//span[@class="price"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(u'<[^<>]+>|\n+|\r+|\t+|  +|["£$]')
            new_data = data_re.sub('', data[0])
            if(data[0].find(u'£') != -1):
                item['list_price'] = self._format_price('GBP', new_data)
            elif(data[0].find('$') != -1):
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


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
