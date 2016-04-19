# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'sexydresses'

class SexydressesSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["sexydresses.com"]

    def __init__(self, *args, **kwargs):
        super(SexydressesSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.sexydresses.com'
        items_xpath = '//*[@class="product-small grid1"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.sexydresses.com'
        nexts_xpath = '//*[@class="page-numbers"]/@href'

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
        item['store_name'] = 'Sexydresses'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Sexydresses'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="product-sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()[len('SKU: #'):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desc_xpath = '//*[@class="content-collateral std"]'
        data = sel.xpath(desc_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//*[@itemprop="image"]/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for img in data:
                imgs.append(img.strip())
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@id="price-box-publicgroup"]/div/p[@class'
            '="old-price"]/span[@class="price"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0 :
            list_price_number = data[0][len('$'):].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

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