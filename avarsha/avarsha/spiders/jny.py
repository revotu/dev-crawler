# -*- coding: utf-8 -*-
# @author: donglongtu

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'jny'

class JnySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["jny.com"]

    def __init__(self, *args, **kwargs):
        super(JnySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.jny.com'
        items_xpath = '//*[@class="innerProductImg"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        next_page_reg = re.compile(r'lazyloadinglinks\[\w*\]=\'(.+?)\'')
        next_page_list = next_page_reg.findall(sel.response.body)
        requests = []
        if len(next_page_list) != 0:
            for url in next_page_list:
                list_urls.append(url)
                requests.append(scrapy.Request(url, callback=self.parse))
            return requests
        else :
            return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Jny'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@itemprop="brand"]/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@itemprop="identifier"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desc_xpath = '//*[@id="descriptionHolder"]'
        data = sel.xpath(desc_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//*[@id="imagesLookupTable"]/@value'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            index = data[0].rfind('{')
            imgs_reg = re.compile(r'(http.+?)\'')
            imgs_list = imgs_reg.findall(data[0][index:])
        item['image_urls'] = imgs_list

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_reg = re.compile(r'\'salesPrice\':\'(.+?)\'')
        data = price_reg.findall(sel.response.body)
        if len(data) != 0:
            price_number = data[0].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_reg = re.compile(r'\'standardPrice\':\'(.+?)\'')
        data = list_price_reg.findall(sel.response.body)
        if len(data) != 0 :
            list_price_number = data[0].strip()
            list_price = self._format_price('USD', list_price_number)
            if list_price != item['price'] :
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