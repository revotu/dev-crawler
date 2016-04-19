# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'buckle'

class BuckleSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["buckle.com"]

    def __init__(self, *args, **kwargs):
        super(BuckleSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.buckle.com'
        items_xpath = '//a[@class="prodDetailLink"]/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.buckle.com'
        nexts_xpath = ('//a[@id="next"]/@href')

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@id="productName"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = "Buckle"

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//td[@data-tn="pdp-spec-brand"]/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()
        else:
            item['brand_name'] = "Buckle"

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@id="numberAndSku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'(?:<[^<>]*>)|\n+|\t+|\r+|[ #]+|Item')
            item['sku'] = data_re.sub('', data[0]).strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="pdescription"]/ul'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_url_xpath = ('//div[@id="carouselItems"]//img/@data-zoom-image')
        imgs_url2_xpath = ('//div[@id="carouselItems"]//img/@src')
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        data2_imgs = sel.xpath(imgs_url2_xpath).extract()
        if(len(data_imgs) != 0):
            for line in data_imgs:
                if(line.find('http:') == -1):
                    line = ''.join(['http:', line])
                imgs.append(line)
        elif(len(data2_imgs) != 0):
            for line in data2_imgs:
                if(line.find('http:') == -1):
                    line = ''.join(['http:', line])
                imgs.append(line)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        amount_xpath = '//span[@id="productPrice"]'
        amount = sel.xpath(amount_xpath).extract()
        if(len(amount) != 0):
            line = amount[0]
            idx1 = line.find('</span>')
            if(idx1 != -1):
                idx2 = line.find('</span>', idx1 + len('</span>'))
                line = line[idx1:idx2]
                data_re = re.compile(r'(?:<[^<>]*>)|\n+|\t+|\r+| +')
                _price = data_re.sub('', line).strip()
                item['price'] = self._format_price('USD', _price)

    def _extract_list_price(self, sel, item):
        amount_xpath = '//span[@id="productPrice"]'
        amount = sel.xpath(amount_xpath).extract()
        if(len(amount) != 0):
            line = amount[0]
            idx1 = line.find('was')
            if(idx1 != -1):
                idx2 = line.find('</span>', idx1)
                if(idx2 != -1):
                    line = line[idx2:]
                    data_re = re.compile(r'(?:<[^<>]*>)|\n+|\t+|\r+| +')
                    _price = data_re.sub('', line).strip()
                    item['price'] = self._format_price('USD', _price)

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
