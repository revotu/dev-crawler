# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'brideside'

class BridesideSpider(AvarshaSpider):
    name = _spider_name
    sku = 0
    allowed_domains = ["brideside.com"]

    def __init__(self, *args, **kwargs):
        super(BridesideSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://shop.brideside.com'
        items_xpath = '//ul[@id="shop"]/li/a[@class="product-link"]/@href'

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
        title_xpath = '//input[@id="productTitle"]/@value'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//input[@id="productVendor"]/@value'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        self.sku += 1
        item['sku'] = self.sku

    def _extract_features(self, sel, item):
        pass
            
    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="tabs"]/div/ul/li[not(a)]/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = [ desc.encode('ascii','replace').replace('?',' ') for desc in data ]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@id="thumbnails"]/a[not(@style)]/@href | //div[@id="thumbnails"]/a[1]/@href'
        data = sel.xpath(img_xpath).extract()
        images = []
        if len(data) != 0:
            for index,img in enumerate(data):
                images.append('http:' + img.replace('large.','1024x1024.') + '#index=' + str(index + 1) + '&sku=' + str(item['sku']))
        item['image_urls'] = images

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//h5[@id="showPrice"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].strip().replace('$', ''))

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