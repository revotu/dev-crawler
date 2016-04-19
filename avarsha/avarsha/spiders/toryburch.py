# -*- coding: utf-8 -*-
# @author: huangjunjie
import re, urllib2, json

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'toryburch'

class ToryburchSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["toryburch.com"]

    def __init__(self, *args, **kwargs):
        super(ToryburchSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.toryburch.com'
        items_xpath = '//div[@class="name"]/a/@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath1 = ('//h1[@class="productname"]/text()')
        data = sel.xpath(title_xpath1).extract()
        title = ""
        if len(data) != 0:
            for tmp in data:
                tmp = tmp.strip()
                title = title + tmp
            item['title'] = title

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'toryburch'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'toryburch'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="styleNum"]/span/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="panelContent"]/text()|//div[@class="panelContent"]/ul'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            desc = "".join(data)
            item['description'] = desc


    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//img[@class="swatchimage"]/@src'
        images = []
        data = sel.xpath(img_xpath).extract()
        for imgs in data:
            imgset = re.sub(r'http:.*\/is\/image\/', '', imgs)
            imgset = imgset.replace('W?$trb_swatch$', '')
            url = 'http://s7d5.scene7.com/is/image/ToryBurchLLC?req=set,json,UTF-8&imageSet={%s}' % imgset
            rep = urllib2.urlopen(url)
            html = rep.read()
            index2 = html.find('(')
            html = html[index2:-1]
            html = tuple(eval(html))
            imgset = html[0]['set']['item']
            baseurl = 'http://s7d5.scene7.com/is/image/'
            for json_data in imgset:
                json_data0 = baseurl + json_data['i']['n'] + '?&hei=2000'
                images.append(json_data0)
        item['image_urls'] = images


    def _extract_colors(self, sel, item):
        color_xpath = '//ul[@class="swatchesdisplay"]//li/a/@title'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//div[contains(@class,"size-variation-holder")]/select//option/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data[1:]

    def _extract_stocks(self, sel, item):
        pass


    def _extract_price(self, sel, item):
        id = item['sku']
        price_xpath0 = ('//div[@id="price-%s"]/div[@class="salesprice standardP"]/text()' % id)
        data = sel.xpath(price_xpath0).extract()
        if len(data) != 0:
            idx = data[0].strip().find('$')
            price_number = data[0].strip()[idx + 1:]
            item['price'] = self._format_price('USD', price_number)





    def _extract_list_price(self, sel, item):
        id = item['sku']
        price_xpath0 = ('//div[@id="price-%s"]/div[@class="standardprice"]/text()' % id)
        data = sel.xpath(price_xpath0).extract()
        if len(data) != 0:
            idx = data[0].strip().find('$')
            price_number = data[0].strip()[idx + 1:]
            item['list_price'] = self._format_price('USD', price_number)


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
