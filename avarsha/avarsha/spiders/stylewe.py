# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'stylewe'

class StyleweSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["stylewe.com"]

    def __init__(self, *args, **kwargs):
        super(StyleweSpider, self).__init__(*args, **kwargs)

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

    def __remove_escape(self, content):
        content = content.replace('\\\"' , '"')
        content = content.replace('\\n' , '')
        content = content.replace('\\/' , '/')
        return content

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//p[@class="product-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        dir_xpath = '//ul[@class="breadcrumb text-capitalize category-breadcrumb"]/li/a/text()'
        data = sel.xpath(dir_xpath).extract()
        if len(data) != 0:
            item['dir1'] = data[1]
            item['dir2'] = data[2]

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//h1[@class="designer-name"]/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        item['sku'] = sel.response.url[sel.response.url.rfind('-') + 1:sel.response.url.rfind('.html')]

    def _extract_features(self, sel, item):
        th_xpath = '//section[@id="product-description"]/p/span[1]/text()'
        th = sel.xpath(th_xpath).extract()
        td_xpath = '//section[@id="product-description"]/p/span[last()]/text()'
        td = sel.xpath(td_xpath).extract()
        if len(th) != 0 and len(td) != 0:
            item['features'] = dict(zip(th,td))
            
    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="product-detail-collapse"]/ul/li/h4[contains(text()[last()],"Product Story")]/../div/section/p/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@id="smallView"]/div/ul/li/a/img/@data-big-src'
        data = sel.xpath(img_xpath).extract()
        images = []
        if len(data) != 0:
            for index,img in enumerate(data):
                images.append(img + '#index=' + str(index + 1) + '&sku=' + str(item['sku']))
        item['image_urls'] = images

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_xpath = '//section[@id="options-size"]/div[@class="options-groups"]/button/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = [ size.strip() for size in data]

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="product-price"]/p[@class="price"]/strong/text()'
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