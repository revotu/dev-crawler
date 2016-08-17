# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json
import urllib2
import os

from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider


_spider_name = 'Alibaba'

class AlibabaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["1688.com"]

    def __init__(self, *args, **kwargs):
        super(AlibabaSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        member_id_reg = re.compile(r'member_id:"(.+?)"')
        data = member_id_reg.findall(sel.response.body)
        if len(data) == 0:
            return []
        member_id = data[0]
        pageIndex = 1
        sku = 1
        requests = []
        while True:
            list_url = 'http://m.1688.com/winport/asyncView?memberId=' + str(member_id) + '&pageIndex=' + str(pageIndex) + '&_async_id=offerlist%3Aoffers'
            content = urllib2.urlopen(list_url).read()
            content = self._remove_escape(content)
            if content.find('offerId') == -1:
                break
            offerId_reg = re.compile(r'offerId=(.+?)"')
            data = offerId_reg.findall(content)
            if len(data) == 0:
                break
            for offerId in data:
                site_name = sel.response.url[sel.response.url.find('://') + len('://'):sel.response.url.find('.1688.com')]
                item_url = 'https://detail.1688.com/offer/%s.html?sitename=%s&sku=%s' % (offerId ,site_name ,sku)
                print item_url
                item_urls.append(item_url)
                request = scrapy.Request(item_url, callback=self.parse_item)
                requests.append(request)
                sku += 1
            pageIndex += 1
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        #http://m.1688.com/winport/asyncView?memberId=b2b-2847846249efc59&pageIndex=20&_async_id=offerlist%3Aoffers

        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        pass

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        pass

    def _extract_sku(self, sel, item):
        pass

    def _extract_features(self, sel, item):
        features_key_xpath = '//div[@id="mod-detail-attributes"]//table/tbody/tr/td[@class="de-feature"]/text()'
        features_value_xpath = '//div[@id="mod-detail-attributes"]//table/tbody/tr/td[@class="de-value"]/text()'
        key = sel.xpath(features_key_xpath).extract()
        value = sel.xpath(features_value_xpath).extract()
        
        if len(key) != 0 and len(value) != 0:
            item['features'] = dict(zip(key,value))
        sitename = sel.response.url[sel.response.url.find('?sitename=') + len('?sitename='):sel.response.url.find('&sku=')]
        sku = sel.response.url[sel.response.url.find('&sku=') + len('&sku='):]
        fd = open(sitename, "a")
        fd.write(sku + ' => ')
        fd.write(json.dumps(item['features'], ensure_ascii=False))
        fd.write("\n")
        fd.close()

    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        sitename = sel.response.url[sel.response.url.find('?sitename=') + len('?sitename='):sel.response.url.find('&sku=')]
        sku = sel.response.url[sel.response.url.find('&sku=') + len('&sku='):]
        image_url_xpath = '//div[@id="desc-lazyload-container"]/@data-tfs-url'
        data = sel.xpath(image_url_xpath).extract()
        if len(data) != 0:
            content = urllib2.urlopen(data[0]).read()
            content = self._remove_escape(content)
            img_reg = re.compile(r'src="(.+?)"')
            data = img_reg.findall(content)
            imgs = []
            if len(data) != 0:
                for img in data:
                    if img.find('http') == -1:
                        img = 'http:' + img
                    if img.find('jpg') == -1 and img.find('png') == -1:
                        continue
                    imgs.append(img)
                item['image_urls'] = [ img + '?index=' + str(index + 1) + '&sku=' + sku + '&dir=' + sitename for index ,img in enumerate(list(set(imgs)))]

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