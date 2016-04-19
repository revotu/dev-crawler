# -*- coding: utf-8 -*-
# author: huangjunjie
import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'bernardboutique'

class BernardboutiqueSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["bernardboutique.com"]

    def __init__(self, *args, **kwargs):
        super(BernardboutiqueSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.bernardboutique.com'
        items_xpath = '//*[@class="dvtTitle"]//a/@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.bernardboutique.com'
        nexts_xpath = '//div[@id="cliDvPh2"]/table/tr/td/a[last()]/@href'
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@class="product_Title"]//span/text()'
        data = sel.xpath(title_xpath).extract()
        title = ' '.join(data)
        item['title'] = title

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'bernardboutique'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//span[@id='
            '"ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_itemBrand"]'
            '/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        url = sel.response.url
        m = re.search(r'item-(?P<sku>.*).aspx', url)
        if m:
            item['sku'] = m.groupdict('sku')['sku']
        else:
            m = re.search(r'item(?P<sku>.*).aspx', url)
            item['sku'] = m.groupdict('sku')['sku']

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//span[@id='
            '"ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_lbItDesc"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            desc = data[0]
            desc = re.sub('<b>Item ID</b> : .*Composition', 'Composition', desc)
            item['description'] = desc

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        img_xpath = '//div[@class="dvtScroll"]/ul//li/a/img/@src'
        data = sel.xpath(img_xpath).extract()
        for small_imgs in data:
            large_imgs = small_imgs.replace('_70.jpg', '_1000.jpg')
            imgs.append(large_imgs)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_list_xpath = ('//select[@id="ctl00_ctl00_ContentPlaceHolder1'
            '_ContentPlaceHolder1_ffnpWucShopItemAddCart1_'
            'ffnpWucShopItemAddCartSize1_ffnpWucShopItemAddCartSizeSel1_ddSize"]'
            '//option/text()')
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data[1:]

    def _extract_stocks(self, sel, item):
        pass

    def _tramsform_price(self, data):
        result = {}
        m = re.search(r'[\d,.]+', data)
        if m:
            result['price'] = m.group()
        else:
            return {}
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
        price_xpath0 = ('//*[@id="ctl00_ctl00_ContentPlaceHolder1'
            '_ContentPlaceHolder1_lbPrice"]/span/text()')
        data = sel.xpath(price_xpath0).extract()
        if len(data) != 0:
            data = data[0].encode('utf-8')
            res = self._tramsform_price(data)
            if 'Currency' in res:
                item['price'] = self._format_price(res['Currency'], res['price'])
            else:
                price_xpath = ('//*[@id="ctl00_ctl00_ContentPlaceHolder1'
                               '_ContentPlaceHolder1_lbPrice"]/text()')
                data = sel.xpath(price_xpath).extract()
                if len(data) != 0:
                    res = self._tramsform_price(data[0])
                    item['price'] = self._format_price(res['Currency'], res['price'])



    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//span[@id="ctl00_ctl00_ContentPlaceHolder1'
            '_ContentPlaceHolder1_lbPrice"]/strike/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data = data[0].encode('utf-8')
            if data.find('£') != -1:
                price_number = data[len('£'):].strip()
                item['list_price'] = self._format_price('GBP', price_number)
            elif data.find('$') != -1:
                price_number = data[len('$'):].strip()
                item['list_price'] = self._format_price('USD', price_number)
            else:
                price_number = data[len('EUR'):].strip()
                item['list_price'] = self._format_price('EUR', price_number)



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
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
