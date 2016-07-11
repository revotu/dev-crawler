# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json
import urllib2

from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider


_spider_name = 'pinkprincess'

class PinkprincessSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["pinkprincess.com"]
    index = 0

    def __init__(self, *args, **kwargs):
        super(PinkprincessSpider, self).__init__(*args, **kwargs)

    #list url pattern:http://www.kingwebtools.com/pink_princess/dynamic_paging/dbresults_ajax.php?section_id=flower-girl-dresses&pr=&pg=1&im=&products_per_page=99999

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.pinkprincess.com/'
        items_xpath = '//div[@class="kwmr-contcell"]/div[@class="kwmr-section-thumbs"]/a/@href'

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
        title_xpath = '//h1[@id="kwmr-pagename"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        self.index += 1
        item['store_name'] = str(self.index)

    def _extract_brand_name(self, sel, item):
        pass

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="kwmr-iteminforight code"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) > 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@itemprop="description"]/ul/li/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) > 0:
            item['description'] = data

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@id="links"]/a/@href'
        data = sel.xpath(img_xpath).extract()
        imgs = []
        if len(data) != 0:
            imgs = [ img + '#index=' + str(index + 1) + '&sku=' + item['store_name'] for index,img in enumerate(data)]
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@id="priceholder"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) > 0:
            item['price'] = data[0].strip()

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