# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json
import urllib2

from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider


_spider_name = 'countertech'

class CountertechSpider(AvarshaSpider):
    name = _spider_name
    brand_list = []
    allowed_domains = ["lumendatabase.org"]

    def __init__(self, *args, **kwargs):
        super(CountertechSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://lumendatabase.org'
        items_xpath = '//ol[@class="results-list"]/li/h3/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'https://lumendatabase.org'
        nexts_xpath = '//nav[@class="pagination"]/span[@class="next"]/a/@href'

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
        brand_xpath = '//section[@class="principal secondary hide"]/h6/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]
            self.brand_list.append(item['brand_name'])
            self.brand_list = list(set(self.brand_list))
        print self.brand_list
        with open('countertech', 'w') as f:
            for brand in self.brand_list:
                f.write(brand + '\n')
        f.close()

    def _extract_sku(self, sel, item):
        pass

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        pass

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