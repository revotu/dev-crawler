# -*- coding: utf-8 -*-
# @author: donglongtu

import re

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'tiffanyrose'

class TiffanyroseSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["tiffanyrose.com"]

    def __init__(self, *args, **kwargs):
        super(TiffanyroseSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.tiffanyrose.com'
        items_xpath = '//div[@id="category_product"]/div/a/@href'

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

    def __remove_escape(self, content):
        content = content.replace('\\\"' , '"')
        content = content.replace('\\n' , '')
        content = content.replace('\\/' , '/')
        return content

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
        pass
            
    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        img_re = re.compile('href : "(.*?)"')
        data = img_re.findall(sel.response.body)
        
        sku_xpath = '//p[@id="product_id_text"]/text()'
        sku_pre = sel.xpath(sku_xpath).extract()
        sku_xpath = '//span[@itemprop="productID"]/text()'
        sku_pos = sel.xpath(sku_xpath).extract()
        sku = sku_pre[0] + sku_pos[0]
        
        if len(data) != 0:
            for index,img in enumerate(data):
                imgs.append('http://www.tiffanyrose.com' + img  + '?index=' + str(index + 1) + '&sku=' + sku)
                
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

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()