# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json
import urllib2

from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider


_spider_name = 'augustajones'

class AugustajonesSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["augustajones.com"]
    index = 0

    def __init__(self, *args, **kwargs):
        super(AugustajonesSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = sel.response.url + '&id='
        items_xpath = '//ul[@id="sortable"]/li/@id'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

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
        self.index += 1
        item['sku'] = str(self.index)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        pid = sel.response.url[sel.response.url.find('&id=') + len('&id='):]
        description_xpath = '//ul[@id="sortable"]/li[@id="%s"]/span/div[@class="product-text"]/text()' % (pid)
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        pid = sel.response.url[sel.response.url.find('&id=') + len('&id='):][len('dress_'):]
        img_url = 'http://www.augustajones.com/zoom.php?id=%s&table=products' % (pid)
        content = urllib2.urlopen(img_url).read()
        content = self._remove_escape(content)
        sel = Selector(text=content)
        img_xpath = '//div[@align="center"]/img/@src'
        data = sel.xpath(img_xpath).extract()
        imgs = []
        if len(data) != 0:
            imgs = [ 'http://www.augustajones.com' + key + '0' for key in data ]
            imgs = [ img + '#index=' + str(index + 1) + '&sku=' + str(item['sku']) for index,img in enumerate(imgs)]
        else :
            img_xpath = '//div[@class="imageContainer"]/img/@src'
            data = sel.xpath(img_xpath).extract()
            if len(data) != 0:
                imgs = [ 'http://www.augustajones.com' + data[0] + '#index=1&sku=' + str(item['sku'])]
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