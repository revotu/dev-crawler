# -*- coding: utf-8 -*-
# author: yangxiao


import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'modaoperandi'

class ModaoperandiSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["modaoperandi.com"]

    def __init__(self, *args, **kwargs):
        super(ModaoperandiSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.modaoperandi.com'
        items_xpath = ('//div[@class="cascading_grid-item"]/@data-url')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        # rewrite the function
        page_xpath = ('//select[@class="page-select"]/option/@value')
        page_num = list(set(sel.xpath(page_xpath).extract()))
        page_urls = [self.start_urls[0] + '?page=' + i for i in page_num]
        requests = []
        for list_url in page_urls:
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//span[@class="product-name"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'modaoperandi'

    def _extract_brand_name(self, sel, item):
        brand_xpath = ('//div[@class="products-show"]/div/@data-brand')
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_path = ('//div[@class="products-show"]/div/@data-id')
        data = sel.xpath(sku_path).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="product-desc"]/* | '
            '//div[@class="product-bullets"]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//div[@class="va-wrapper"]/div/@href |'
            '//span[@class="cloud-zoom cursor-pointer"]/@href')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        item['colors'] = \
            re.findall('"product_color":\["(.+?)"\]', sel.response.body)

    def _extract_sizes(self, sel, item):
        size_xpath = ('//div[@id="dk1-size"]/ul/li/@data-value')
        size_list = sel.xpath(size_xpath).extract()
        if len(size_list) != 0:
            item['sizes'] = size_list[1:]

    def _extract_stocks(self, sel, item):
        pass

    def _extract_prices(self, sel, item):
        self._extract_list_price(sel, item)
        self._extract_price(sel, item)
        self._extract_low_price(sel, item)
        self._extract_high_price(sel, item)

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@id="product-info"]/div[@class="prod-price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            if item.get('list_price') != None:
                price_number = data[1].replace('$', '')
                item['price'] = self._format_price("USD ", price_number)
            else:
                price_number = data[0].replace('$', '')
                item['price'] = self._format_price("USD ", price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@id="product-info"]/div[@class="prod-price"]'
            '/span[1]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            if 'DEPOSIT' not in data[0]:
                price_number = data[0].replace('$', '')
                item['list_price'] = self._format_price("USD ", price_number)

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
