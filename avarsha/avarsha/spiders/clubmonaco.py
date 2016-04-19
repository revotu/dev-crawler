# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'clubmonaco'

class ClubmonacoSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["clubmonaco.com"]

    def __init__(self, *args, **kwargs):
        super(ClubmonacoSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.clubmonaco.com'
        items_xpath = '//dt[@class="product-details-a"]/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.clubmonaco.com'
        nexts_xpath = '//a[@class="enabled next"]/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="product-title fn"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Club Monaco'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Club Monaco'

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@class="style"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'Style|[ #:]')
            item['sku'] = data_re.sub('', data[0]).strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="tab-details"]'
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
        url1 = 'http://s7d2.scene7.com/is/image/ClubMonacoGSI/'
        url2 = '?wid=1650&hei=1650'
        for line in sel.response.body.split('\n'):
            if(line.find('zoomImageURL: "') != -1):
                data_re = re.compile(r'\t+| +')
                line = data_re.sub('', line).strip()
                idx1 = line.find('"')
                line = line[idx1 + 1:]
                if(line[0] == 'p'):
                    idx2 = line.find('",')
                    zoomImageURL = line[:idx2]
                    image_url = ''.join([url1, zoomImageURL, url2])
                    imgs.append(image_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price1_xpath = '//div[@class="money"]/span[@class="sale-price"]/text()'
        price2_xpath = '//div[@class="money"]/span/text()'
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
        list_price_xpath = '//div[@class="money"]/span\
            [@class="base-price"]/text()'
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
