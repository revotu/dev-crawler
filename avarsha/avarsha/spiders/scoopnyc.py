# -*- coding: utf-8 -*-
# @author: huangjunjie
import re, json, urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'scoopnyc'

class ScoopnycSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["scoopnyc.com"]

    def __init__(self, *args, **kwargs):
        super(ScoopnycSpider, self).__init__(*args, **kwargs)


    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = 'http://www.scoopnyc.com'
        items_xpath = '//div[@class="section-body"]/noscript/a/@href'
        return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath1 = ('//div[@class="section-description-head"]'
            '/h2/text()|//div[@class="section-description-head"]/h3/text()')
        data = sel.xpath(title_xpath1).extract()
        if len(data) != 0:
            title = ''.join(data)
            item['title'] = title


    def _extract_store_name(self, sel, item):
        item['store_name'] = 'scoopnyc'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//div[@class="section-description-head"]/h2/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//p[@class="product-id"]//text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            m = re.search(r'# (?P<sku>\w*)', data[0])
            if m:
                item['sku'] = m.groupdict('sku')['sku']

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="description-body"]/p'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            desc = "".join(data)
            item['description'] = desc


    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//div[@class="section-image-inner"]/ul/li/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for small_img in data:
                imgs.append(small_img.replace('1100x1451/', ''))
        item['image_urls'] = imgs

    def _get_json(self, sel):
        json_xpath = '//script[@type="text/javascript"]/text()'
        data = sel.xpath(json_xpath).extract()
        for i in data:
            m = re.search(r'tree = (?P<json>.*);', i)
            if m:
                my_json = m.groupdict('json')['json']
                my_json = my_json.encode('utf8')
                res_json = json.loads(my_json)
                return res_json

    def _extract_colors(self, sel, item):
        res_json = self._get_json(sel)
        colors = []
        color_json = res_json['attributes_new']['colr']['children']
        for i in color_json.keys():
            colors.append(color_json[i]['label'])
        item['colors'] = colors

    def _extract_sizes(self, sel, item):
        res_json = self._get_json(sel)
        _sizes = []
        size_json = res_json['attributes_new']['size1']['children']
        for i in size_json.keys():
            _sizes.append(size_json[i]['label'])
        item['sizes'] = _sizes


    def _extract_stocks(self, sel, item):
        pass


    def _extract_price(self, sel, item):
        res_json = self._get_json(sel)
        item['price'] = self._format_price('USD', res_json['basePrice'])

    def _extract_list_price(self, sel, item):
        res_json = self._get_json(sel)
        oldprice = res_json['oldPrice']
        baseprice = res_json['basePrice']
        if oldprice != baseprice:
            item['list_price'] = self._format_price('USD', oldprice)

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
