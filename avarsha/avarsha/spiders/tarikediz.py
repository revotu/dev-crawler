# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json
import urllib2

from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider


_spider_name = 'tarikediz'

class TarikedizSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["tarikediz.com"]
    index = 0

    def __init__(self, *args, **kwargs):
        super(TarikedizSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = sel.response.url
        items_xpath = '//div[@class="Collection_Group"]/@id'

        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + '/Details/' + path
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = ''

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
        item['sku'] = sel.response.url[sel.response.url.find('Collection/') + len('Collection/'):sel.response.url.find('/Details')]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@class="Detail_Image"]//img/@src'
        data = sel.xpath(img_xpath).extract()
        base_url = 'http://www.tarikediz.com'
        imgs = []
        name = sel.response.url.split('/')[-1]
        if len(data) > 0:
            imgs = [ base_url + img.replace('medium','large') + '#index=' + str(index + 1) + '&sku=' + item['sku'] + '&dir=' + name for index,img in enumerate(data)]
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