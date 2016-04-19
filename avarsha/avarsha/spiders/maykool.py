# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

from avarsha_spider import AvarshaSpider

_spider_name = 'maykool'

class MaykoolSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["maykool.com"]

    def __init__(self, *args, **kwargs):
        super(MaykoolSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@class="products-grid"]//a//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="pages"]//li//a//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="product-name"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Maykool'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Maykool'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][len('SKU: '):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="short-description"]'
                             '/div[@class="std"]/text()')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        image_url_xpath = ('//div[@class="product-img-box"]'
                        '//div[@id="zoomWrapper"]//a//@href')
        data = sel.xpath(image_url_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        special_price_xpath = ('//div[@class="price-box"]'
            '/p[@class="special-price"]/span[@class="price"]/text()')
        regular_price_xpath = ('//div[@class="price-box"]'
            '/span[@class="regular-price"]/span[@class="price"]/text()')
        data = sel.xpath(regular_price_xpath).extract()
        if len(data) != 0:
            price_str = data[0].strip()
            item['price'] = price_str.replace('$', 'USD ')
        else:
            data = sel.xpath(special_price_xpath).extract()
            if len(data) != 0:
                price_str = data[0].strip()
                item['price'] = price_str.replace('$', 'USD ')

    def _extract_list_price(self, sel, item):
        price_xpath = ('//div[@class="price-box"]/p[@class="old-price"]'
                       '/span[@class="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_str = data[0].strip()
            item['list_price'] = price_str.replace('$', 'USD ')

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
