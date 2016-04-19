# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'farfetch'

class FarfetchSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["farfetch.com"]

    def __init__(self, *args, **kwargs):
        super(FarfetchSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if idx1 != -1:
            return url[:idx1]
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.farfetch.com'
        items_xpath = '//div[@class="listing-item-content-box"]//a//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.farfetch.com'
        nexts_xpath = ('//div[@data-tstid="ListingBox_Page"]'
            '/ul[@class="list-regular absolute"]//li//a//@href')

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h2[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Farfetch'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//h1[@itemprop="brand"]/a/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()
        else:
            item['brand_name'] = 'Farfetch'

    def _extract_sku(self, sel, item):
        for line in sel.response.body.split('\n'):
            idx1 = line.find('productId: ')
            if idx1 != -1:
                idx2 = line.find(',')
                if idx2 != -1:
                    item['sku'] = line[idx1 + len('productId: '):idx2]
                    break

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = (
            '//div[@data-tstid="Content_Description"]/p[1]/text()')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        for line in sel.response.body.split(' '):
            idx1 = line.find('data-fullsrc=\"')
            if idx1 != -1:
                idx2 = line.find('\" ', idx1)
                img_url = line[idx1 + len('data-fullsrc=\"'):idx2].strip()
                imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price1_xpath = '//span[@class="color-red listing-sale"]/text()'
        price2_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price1_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD ', price_number)
        else:
            data = sel.xpath(price2_xpath).extract()
            if len(data) != 0:
                price_number = data[0][len('$'):].strip()
                item['price'] = self._format_price('USD ', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="strike listing-price"]/span/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['list_price'] = self._format_price('USD ', price_number)

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
