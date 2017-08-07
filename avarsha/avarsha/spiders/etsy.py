# -*- coding: utf-8 -*-
# @author: donglongtu

import sys
sys.path.append(r'D:\work\dev-crawler\avarsha')

import scrapy.cmdline
import urllib
import re
import json
import math

from w3lib.html import remove_tags
from avarsha_spider import AvarshaSpider
from scrapy.selector import Selector
from openpyxl import load_workbook

_spider_name = 'etsy'

class EtsySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["etsy.com"]
    brand_list = []

    def __init__(self, *args, **kwargs):
        super(EtsySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        
        base_url = ''
        items_xpath = '//div[@class="js-merch-stash-check-listing block-grid-item listing-card position-relative parent-hover-show"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//nav[@role="navigation"]/a[last()]/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        return
        title_xpath = '//span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = sel.response.url[sel.response.url.find('https://www.etsy.com/shop/') + len('https://www.etsy.com/shop/'): sel.response.url.find('/reviews')]

    def _extract_brand_name(self, sel, item):
        return
        brand_reg = re.compile(r'"shop_name":"(.+?)"')
        data = brand_reg.findall(sel.response.body)
        if len(data) != 0:
            item['brand_name'] = data[0].strip()
            # self.brand_list.append(item['brand_name'])
            # self.brand_list = list(set(self.brand_list))
            # print self.brand_list
            # fd = open('brand', "w")
            # for brand in self.brand_list:
            #     fd.write("%s\n" % brand)
            # fd.close()

    def _extract_sku(self, sel, item):
        return
        item['sku'] = sel.response.url[sel.response.url.find('listing/') + len('listing/'): sel.response.url.rfind('/')]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        return
        desc_xpath = '//div[@id="item-overview"]/ul/li/node()'
        data = sel.xpath(desc_xpath).extract()
        if len(data) != 0:
            data = [remove_tags(v.strip()) for v in data]
            description = ';'.join(data).replace(':;',':').replace('from;','from ')
            item['description'] = description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        return
        dir = item['brand_name']
        imgs_xpath = '//ul[@id="image-carousel"]/li/@data-full-image-href'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = [ img + '?index=' + str(index + 1) + '&sku=' + item['sku'] + '&dir=' + dir for index ,img in enumerate(list(set(data)))]

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        return
        price_xpath = '//meta[@property="etsymarketplace:price_value"]/@content'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
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

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        #review need nickname and content and custom pic
        review_url_prefix = sel.response.url
        
        review_list = []
        item['image_urls'] = []
        pagenum = 1
        count_xpath = '//div[@class="text-center"]/nav[@role="navigation"]/a/@data-page'
        data = sel.xpath(count_xpath).extract()
        if len(data) > 0:
            data = [int(v) for v in data]
            pagenum = max(data)
        
        page = 1
        
        review_url = review_url_prefix + '?ref=pagination&page=1'
        
        while page <= pagenum:
            content = urllib.urlopen(review_url).read()
            sel = Selector(text=content)
            review_div_xpath = '//div[@data-region="review-list"]/div[@data-region="review"]'
            review_div = sel.xpath(review_div_xpath).extract()

            if len(review_div) > 0:
                for review in review_div:
                    sel = Selector(text=review)
                    review_name_xpath = '//div[@class="mt-xs-2 mb-xs-2"]/p/a/text()'
                    review_date_xpath = '//div[@class="mt-xs-2 mb-xs-2"]/p/text()'
                    review_content_xpath = '//div[@class="text-gray-lighter"]/p/text()'
                    review_sku_xpath = '//div[@class="flag-body hide-xs hide-sm"]/p/a/@href'
                    review_img_xpath = '//img/@data-ap-src'
                    review_name = sel.xpath(review_name_xpath).extract()
                    review_content = sel.xpath(review_content_xpath).extract()
                    review_sku = sel.xpath(review_sku_xpath).extract()
                    review_img = sel.xpath(review_img_xpath).extract()
                    review_date = sel.xpath(review_date_xpath).extract()
                    if len(review_name) > 0 and  len(review_content) > 0 and len(review_sku) > 0:
                        sku = review_sku[0][review_sku[0].find('/listing/') + len('/listing/'):review_sku[0].rfind('/')] 
                        review_list.append({'sku': sku,'name':review_name[0],'content':review_content[0],'date':review_date[1].strip()})
                    if len(review_img) > 0 and len(review_sku) > 0:
                        for index,img in enumerate(review_img):
                            item['image_urls'].append(img + '?index=' + str(index + 1) + '&sku=' + str(sku) + '&dir=' + item['store_name'])
                        
            page += 1
            review_url = review_url_prefix + '?ref=pagination&page=%d' % (page)
            
            review_name = []
            review_content = []
            review_sku = []

        item['review_list'] = review_list
            

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
