# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json
import urllib2
import urllib

from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider


_spider_name = 'herabridal'

class BrideandcoSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["herabridal.co.nz"]
    index = 0

    def __init__(self, *args, **kwargs):
        super(BrideandcoSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = ''

        # don't need to change this line
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
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        pid_xpath = '//a[@class="mg_seo_dl_link"]/@href'
        data = sel.xpath(pid_xpath).extract()
        img_url = sel.response.url
        imglist = []
        if len(data) != 0:
            pids = [ key[key.rfind('mg_ld_') + len('mg_ld_'):] for key in data]
            for pid in pids:
                query_args = {'mg_lb':'mg_lb_content','pid':pid}
                encoded_args = urllib.urlencode(query_args)
                content = urllib2.urlopen(img_url,encoded_args).read()
                content = self._remove_escape(content)
                sel = Selector(text=content)
                img_xpath = '//div[@class="mg_item_featured"]//a/@href'
                data = sel.xpath(img_xpath).extract()
                imgs = []
                imgback = []
                if len(data) != 0:
                    imgs = [ img + '#index=' + str(index + 1) + '&sku=' + pid for index,img in enumerate(data)]
                    for i in imgs:
                        if i.find('http') == -1:
                            imgback.append('http:' + i)
                        else :
                            imgback.append(i)
                imglist += imgback
                print imglist
        item['image_urls'] = imglist

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