# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

import re

from w3lib.html import remove_tags
from avarsha_spider import AvarshaSpider


_spider_name = 'ebay'

class EbaySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["ebay.com"]

    def __init__(self, *args, **kwargs):
        super(EbaySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = ''
        items_xpath = '//div[@class="gvtitle"]/h3/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        base_url = ''
        nexts_xpath = '//td[@class="pages"]//a//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//meta[@property="og:title"]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        pass

    def _extract_sku(self, sel, item):
        sku_xpath = '//a[contains(@data-itemid, "")]/@data-itemid'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="itemAttr"]/div[@class="section"]/table//tr/node()'
        data = sel.xpath(description_xpath).extract()
        if len(data) > 0 :
            data = [remove_tags(v).strip().replace('\t','').replace('\n','')  for v in data]
            data = filter(None,data)
            description = ''
            for index,desc in enumerate(data):
                if index % 2 == 0:
                    description += desc
                else :
                    description += desc + ';'
            item['description'] = description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        dir = 'ebay'
        img_reg = re.compile(r'"maxImageUrl":"(.+?)"')
        data = img_reg.findall(sel.response.body)

        if len(data) != 0:
            data = list(set(data))
            item['image_urls'] = [ img.replace('\u002F','/') + '?index=' + str(index + 1) + '&sku=' + item['sku'] + '&dir=' + dir for index ,img in enumerate(list(set(data)))]

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_reg = re.compile(r'"binPriceOnly":"(.+?)"')
        data = price_reg.findall(sel.response.body)
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

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass

def main():
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
