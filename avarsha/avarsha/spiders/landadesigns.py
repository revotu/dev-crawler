# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json
import urllib2

from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'landadesigns'

class LandadesignsSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["landadesigns.com"]
    index = 0

    def __init__(self, *args, **kwargs):
        super(LandadesignsSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@class="centerBoxContentsProducts centeredContent back"]/a/@onclick'

        item_nodes = sel.xpath(items_xpath).extract()
        item_nodes = [ item[item.find("'") + 1: item.rfind("'")] for item in item_nodes]
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@id="productsListingListingTopLinks"]/a[@title=" Next Page "]/@href'

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
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        pid = sel.response.url[sel.response.url.find('&products_id=') + len('&products_id='):sel.response.url.rfind('&cherryoneid')]
        img_url = 'http://landadesigns.com/index.php?main_page=popup_image&pID=' + pid + '#index=' + '1' + '&sku=' + str(item['sku'])
        content = urllib2.urlopen(img_url).read()
        content = self._remove_escape(content)
        sel = Selector(text=content)
        img_xpath = '//img/@src'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            img_url = 'http://landadesigns.com/' + data[0] + '#index=' + '1' + '&sku=' + str(item['sku'])
        item['image_urls'] = [img_url]

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