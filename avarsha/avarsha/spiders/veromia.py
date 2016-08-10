# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json
import urllib2

from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider


_spider_name = 'veromia'

class VeromiaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["veromia.co.uk"]
    index = 0

    def __init__(self, *args, **kwargs):
        super(VeromiaSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = ''

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
        self.index += 1
        item['store_name'] = str(self.index)

    def _extract_brand_name(self, sel, item):
        pass

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
        dir = sel.response.url[sel.response.url.rfind('/') + 1:sel.response.url.find('.html')]
        url_xpath = '//frame[@name="main"]/@src'
        data = sel.xpath(url_xpath).extract()
        sku = 1
        imgs = []
        if len(data) > 0:
            url = data[0]
            response = urllib2.urlopen(url)
            content = urllib2.urlopen(url).read()
            content = self._remove_escape(content)
            sel = Selector(text=content)
            
            num_reg = re.compile(r'1 of (.+?) styles')
            num_set = num_reg.findall(sel.response.body)
            num = int(num_set[0])
            while True:
                data = []
                img_xpath = '//a[@class="MagicZoomPlus"]/img/@src'
                data = sel.xpath(img_xpath).extract()
                if len(data) > 0:
                    for img in data:
                        imgs.append(img.replace('styles-medium','big') + '#index=' + str(1) + '&sku=' + str(sku) + '&dir=' + dir)
                        sku += 1
                        print sku,num
                if sku >= num:
                    break
                #print sel.response.body
                next_reg = re.compile(r'href=\'(.+?)\'.+?next style')
                next_set = next_reg.findall(sel.response.body)
                if len(next_set) > 0:
                    url = next_set[0]
                    content = urllib2.urlopen(url).read()
                    content = self._remove_escape(content)
                    sel = Selector(text=content)
            print imgs
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