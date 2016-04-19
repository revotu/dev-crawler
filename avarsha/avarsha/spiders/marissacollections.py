# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re
import urllib2
import lxml.html as LH

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'marissacollections'

class MarissacollectionsSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["marissacollections.com"]
    flag = False

    def __init__(self, *args, **kwargs):
        super(MarissacollectionsSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@class="category-products"]//a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        if(self.flag == True):
            return requests
        pageNum = 1
        last_page = 1
        while(True):
            self.flag = True
            _count, content = self._get_content(pageNum, sel)
            pageNum += 1
            if(_count == 3):
                continue
            doc = LH.fromstring(content)
            current_page = doc.xpath(
                '//div[@class="pages"]//li[@class="current"]/text()')
            if(current_page[0] != last_page):
                last_page = current_page[0]
                urls = doc.xpath('//div[@class="category-products"]//a/@href')
                for item_url in urls:
                    list_urls.append(item_url)
                    requests.append(
                        scrapy.Request(item_url, callback=self.parse_item))
            else:
                break
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="product-name std"]/h2/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Marissacollections'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Marissacollections'

    def _extract_sku(self, sel, item):
        sku_xpath = '//p[@class="product-ids"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'SKU|[ #]')
            item['sku'] = str(data_re.sub('', data[0]).strip())

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="details"]/div'
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
        imgs_url_xpath = '//div[@class="more-views"]/ul[1]//a/@rel'
        imgs_url_default_xpath = '//p[@class="product-image"]/img/@src'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        data_default_imgs = sel.xpath(imgs_url_default_xpath).extract()
        if(len(data_imgs) != 0):
            for line in data_imgs:
                idx1 = line.find("largeimage: '")
                if(idx1 != -1):
                    idx2 = line.find("'}", idx1 + len("largeimage: '"))
                    image_url = line[idx1 + len("largeimage: '"):idx2]
                    imgs.append(image_url)
                else: break
        elif(len(data_default_imgs) != 0):
            imgs.append(data_default_imgs[0])
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price1_xpath = '//p[@class="special-price"]/span[@class="price"]/text()'
        price2_xpath = '//span[@class="regular-price"]/\
            span[@class="price"]/text()'
        price1 = sel.xpath(price1_xpath).extract()
        price2 = sel.xpath(price2_xpath).extract()
        if(len(price1) != 0):
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['price'] = self._format_price('USD', \
                data_re.sub('', price1[0]).strip())
        if(len(price2) != 0):
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['price'] = self._format_price('USD', \
                data_re.sub('', price2[0]).strip())

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//p[@class="old-price"]/span[@class="price"]/text()'
        list_price = sel.xpath(list_price_xpath).extract()
        if(len(list_price) != 0):
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['list_price'] = self._format_price('USD', \
                data_re.sub('', list_price[0]).strip())

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        is_free_shipping_xpath = '//dl[@class="extra-info"]//p/text()'
        _is_free_shipping = sel.xpath(is_free_shipping_xpath).extract()
        if(len(_is_free_shipping) != 0):
            for line in _is_free_shipping:
                if(line.find('free ground shipping') != -1):
                    item['is_free_shipping'] = True
                    break

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass

    def _get_content(self, pageNum, sel):
        base_url = sel.response.url
        url2 = '&page='
        if(base_url.find('?') == -1):
            url2 = '?page='
        url3 = '&is_ajax=1&p='
        url2 = url2 + str(pageNum)
        url3 = url3 + str(pageNum + 1)
        request_url = base_url + url2 + url3
        req = urllib2.Request(request_url)
        response = urllib2.urlopen(req)
        return self._try_read_content(response)

    def _try_read_content(self, response):
        _count = 0
        content = ''
        while True:
            try:
                content = response.read()
            except :
                log.msg("Error: can\'t read data or IncompleteRead.", log.DEBUG)
                if _count == 3:
                    log.msg("Has tried 3 times. Give up.", log.DEBUG)
                    break
                _count = _count + 1
                continue
            else:
                break
        return _count, self._remove_escape(content)

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
