# -*- coding: utf-8 -*-
# @author: huangjunjie
import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'moschino'

class MoschinoSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["moschino.com"]

    def __init__(self, *args, **kwargs):
        super(MoschinoSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.moschino.com'
        items_xpath = '//div[contains(@class,"product")]/a/@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath1 = ('//h1[@class="product-title"]/span/text()')
        data = sel.xpath(title_xpath1).extract()
        if len(data) != 0:
            item['title'] = data[0]


    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Moschino'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Moschino'

    def _extract_sku(self, sel, item):
        url = sel.response.url
        m = re.search(r'_cod(?P<sku>\w*).html', url)
        if m:
            item['sku'] = m.groupdict('sku')['sku']

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@id="itemDesc_container"]'
        data = sel.xpath(description_xpath).extract()
        print data
        if len(data) != 0:
            desc = "".join(data)
            item['description'] = desc


    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//ul[@id="zoomAlternateImageList"]//li/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        for img in data:
            imgs.append(img)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//*[@id="itemColorsContainer"]/ul//li/@title'
        data = sel.xpath(color_xpath).extract()
        colors = []
        for color in data:
            colors.append(color)
        item['colors'] = colors

    def _extract_sizes(self, sel, item):
        size_xpath = '//*[@id="itemsizesContainer"]/ul//li/span/text()'
        data = sel.xpath(size_xpath).extract()
        sizes = []
        for size in data:
            sizes.append(size)
        item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass


    def _extract_price(self, sel, item):
        price_xpath0 = ('//div[@class="itemBoxPrice"]/span/text()')
        data = sel.xpath(price_xpath0).extract()
        if len(data) != 0:
            idx = data[0].strip().find('$')
            price_number = data[0].strip()[idx + 1:]
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = ('//div[@class="newprice"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                idx = data[0].strip().find('$')
                price_number = data[0].strip()[idx + 1:]
                item['price'] = self._format_price('USD', price_number)




    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="oldprice"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            idx = data[0].strip().find('$')
            price_number = data[0].strip()[idx + 1:]
            item['list_price'] = self._format_price('USD', price_number)


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
