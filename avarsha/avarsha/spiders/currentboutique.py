# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'currentboutique'

class CurrentboutiqueSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["currentboutique.com"]

    def __init__(self, *args, **kwargs):
        super(CurrentboutiqueSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@class="ProductImage"]/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.currentboutique.com/'
        nexts_xpath = ('//div[@class="SearchContainer"][1]'
            '//div[@class="FloatLeft Next"]/a/@href')
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            idx = list_url.find('#')
            if(idx != -1):
                list_url = list_url[:idx]
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="ProductMain"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Current Boutique'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@class="ProductDetailsGrid"]/div[3]//a/text()'
        _brand_name = sel.xpath(brand_name_xpath).extract()
        if(len(_brand_name) != 0):
            item['brand_name'] = _brand_name[0]

    def _extract_sku(self, sel, item):
        sku = ''
        for line in sel.response.body.split('\n'):
            idx1 = line.find('productId =')
            if(idx1 != -1):
                idx2 = line.rfind(';')
                sku = line[idx1 + len('productId ='):idx2].strip()
        item['sku'] = sku

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class=\
            "ProductDescriptionContainer prodAccordionContent"]//ul'
        data = sel.xpath(description_xpath).extract()
        _description = ''
        if len(data) != 0:
            _description = ''.join([_description, data[0]])
        item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_url_xpath = '//div[@class="ProductTinyImageList2"]'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        if(len(data_imgs) != 0):
            line = data_imgs[0]
            while(True):
                idx1 = line.find('"largeimage": "')
                if(idx1 != -1):
                    idx2 = line.find('"}', idx1 + len('"largeimage": "'))
                    image_url = line[idx1 + len('"largeimage": "'):idx2]
                    imgs.append(image_url)
                    line = line[idx2:]
                else: break
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//em[@class="ProductPrice VariationProductPrice"]/text()'
        price = sel.xpath(price_xpath).extract()
        if(len(price) != 0):
            data_re = re.compile(r'(?:<[^<>]>)+|[$]')
            item['price'] = self._format_price(
                'USD', data_re.sub('', price[0]).strip())

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="DetailRow RetailPrice"]/strike/text()'
        list_price = sel.xpath(list_price_xpath).extract()
        if(len(list_price) != 0):
            data_re = re.compile(r'(?:<[^<>]>)+|[$]')
            item['list_price'] = self._format_price(
                'USD', data_re.sub('', list_price[0]).strip())

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
