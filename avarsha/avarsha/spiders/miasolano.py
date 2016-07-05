# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json

from avarsha_spider import AvarshaSpider


_spider_name = 'miasolano'

class MiasolanoSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["miasolano.com"]
    index = 0

    def __init__(self, *args, **kwargs):
        super(MiasolanoSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//ul[@class="ProductList "]/li/div[@class="productHover"]/div[@class="Inner"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="FloatLeft Next"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        pass

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        pass

    def _extract_sku(self, sel, item):
        self.index += 1
        item['sku'] = self.index

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        item_xpath = '//div[@class="ProductDescriptionContainer"]/p/span/text()'
        data = sel.xpath(item_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@class="ProductTinyImageList2"]//div[@class="TinyOuterDiv"]/div/a/@rel'
        data = sel.xpath(img_xpath).extract()
        imgs = []
        if len(data) != 0:
            suffix = 1
            for rel in data:
                img = json.loads(rel)['largeimage']
                img_url = img + '#index=' + str(suffix) + '&sku=' + str(item['sku'])
                suffix += 1
                imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        pass

    def _extract_list_price(self, sel, item):
        pass

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