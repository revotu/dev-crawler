# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'mytheresa'

class MytheresaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["mytheresa.com"]

    def __init__(self, *args, **kwargs):
        super(MytheresaSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.mytheresa.com'
        items_xpath = '//*[@class="category-products"]/ul/li/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.mytheresa.com'
        nexts_xpath = '//*[@class="next i-next"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Mytheresa'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@itemprop="brand"]/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="sku-number"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = ('//*[@class="items noscroller"]/a[@rel="zoom-id:main-image'
            '; show-title:false; group: main;"]/@href'
            ' | //*[@class="items "]/a[@rel="zoom-id:main-image; '
            'show-title:false; group: main;"]/@href')
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        stocks_xpath = '//*[@itemprop="availability"]/@content'
        data = sel.xpath(stocks_xpath).extract()
        if len(data) != 0 and data[0].strip() != 'in_stock':
            item['stocks'] = 0

    def _extract_price(self, sel, item):
        price_xpath = ('//*[@class="product-main-info"]//span[@class="regular'
            '-price"]/span[@class="price"]/text() | '
            '//*[@class="product-main-info"]/div[@class="price-box "]/p[@class'
            '="special-price"]/span[@class="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[2:]
            item['price'] = self._format_price('EUR', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@class="product-main-info"]/div[@class="price'
            '-box "]/p[@class="old-price"]/span[@class="price"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()[2:]
            item['list_price'] = self._format_price('EUR', list_price_number)

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