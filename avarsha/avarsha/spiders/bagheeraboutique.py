# -*- coding: utf-8 -*-
# @author: huangjunjie
import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'bagheeraboutique'

class BagheeraboutiqueSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["bagheeraboutique.com"]

    def __init__(self, *args, **kwargs):
        super(BagheeraboutiqueSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.bagheeraboutique.com'
        items_xpath = '//div[@class="text"]/a/@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        base_url = sel.response.url
        nexts_xpath = '//*[@id="resultWrap"]//div[@class="pagination"]/a/@href'
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath0 = ('//h2[@itemprop="brand"]/span[@itemprop="name"]/text()')
        data = sel.xpath(title_xpath0).extract()
        if len(data) != 0:
            title = data[0]
        title_xpath1 = ('//h1[@itemprop="name"]/text()')
        data = sel.xpath(title_xpath1).extract()
        if len(data) != 0:
            title = title + data[0]
        item['title'] = title

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'bagheeraboutique'

    def _extract_brand_name(self, sel, item):
        brand_xpath = ('//h2[@itemprop="brand"]//span[@itemprop="name"]/text()')
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            brand = data[0]
        item['brand_name'] = brand

    def _extract_sku(self, sel, item):
        url = sel.response.url
        m = re.search(r'/product/(?P<sku>\w*)', url)
        if m:
            item['sku'] = m.groupdict('sku')['sku']

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@itemprop="description"]/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            desc = ""
            for desc_part in data:
                desc = desc + desc_part
            item['description'] = desc


    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//div[@class="photo-scroller"]/ol//a/@href'
        data = sel.xpath(imgs_xpath).extract()
        for img in data:
            imgs.append(img)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_xpath = '//div[@class="sizes"]/ul//li/label/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _tramsform_price(self, data):
        result = {}
        m = re.search(r'[\d,.]+', data)
        result['price'] = m.group()
        if  data.find('$') != -1:
            result['Currency'] = 'USD'
        elif data.find('£') != -1:
            result['Currency'] = 'GBP'
        elif data.find('€') != -1:
            result['Currency'] = 'EUR'
        elif data.find('¥') != -1:
            result['Currency'] = 'JPY'
        elif data.find('₩') != -1:
            result['Currency'] = 'KRW'
        elif data.find('IDR') != -1:
            result['Currency'] = 'IDR'
        elif data.find('A$') != -1:
            result['Currency'] = 'UAD'
        elif data.find('C$') != -1:
            result['Currency'] = 'CAD'
        return result

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@itemprop="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        for price_data in data:
            price = price_data.strip()
            if len(price) != 0:
                price = price.encode('utf-8')
                res = self._tramsform_price(price)
                item['price'] = self._format_price(res['Currency'], res['price'])



    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@itemprop="price"]/span[@class="old"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price = data[0].strip()
            price = price.encode('utf-8')
            res = self._tramsform_price(price)
            item['list_price'] = self._format_price(res['Currency'], res['price'])


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
