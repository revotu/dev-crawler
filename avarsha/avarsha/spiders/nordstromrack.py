# -*- coding: utf-8 -*-
# author: tanyafeng

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'nordstromrack'

class NordstromrackSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["nordstromrack.com"]

    def __init__(self, *args, **kwargs):
        super(NordstromrackSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.nordstromrack.com'
        items_xpath = '//*[@class="catalog-grid-product"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'https://www.nordstromrack.com'
        nexts_xpath = '//*[@class="next"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@property="og:title"]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Nordstromrack'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@property="og:brand"]/@content'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="fp-root"]/@data-product-id'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="js-accordion__section-content"]/div/node()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//*[@property="og:image"]/@content'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//*[@data-bind="text: visibleColorName"]/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//*[@class="new-selector__text"]/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        currency_xpath = '//*[@property="og:price:currency"]/@content'
        price_xpath = '//*[@property="og:price:amount"]/@content'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            if data[0].find('-') != -1:
                price_str = data[0].split('-')
                price_number = price_str[0].strip()
            else:
                price_number = data[0].strip()
            currency_data = sel.xpath(currency_xpath).extract()
            if len(currency_data) != 0:
                item['price'] = self._format_price(currency_data[0], \
                    price_number)

    def _extract_list_price(self, sel, item):
        currency_xpath = '//*[@property="og:price:currency"]/@content'
        list_price_xpath = '//*[@property="og:price:standard_amount"]/@content'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            if data[0].find('-') != -1:
                list_price_str = data[0].split('-')
                list_price_number = list_price_str[0].strip()
            else:
                list_price_number = data[0].strip()
            currency_data = sel.xpath(currency_xpath).extract()
            if len(currency_data) != 0:
                item['list_price'] = self._format_price(currency_data[0], \
                    list_price_number)

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
    scrapy.cmdline.execute(
        argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
