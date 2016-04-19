# -*- coding: utf-8 -*-
# author: huoda

import urllib2

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'italist'

class ItalistSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["italist.com"]
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'

    def __init__(self, *args, **kwargs):
        super(ItalistSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('user-agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@id="product_list"]/div/a//@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        requests = []

        flag = self.start_urls[0].find('?q')
        if flag != -1:
            url1 = self.start_urls[0][:flag]
            tab = self.start_urls[0][flag + 1:]
            url2 = '?categories%5B%5D=1&sort_field=pv_insert_time&'
            url3 = '&limit=60&skip='
            url4 = '&partner='
            skip = 0
            products_url = url1 + url2 + tab + url3 + str(skip) + url4
            req = urllib2.Request(products_url)
            req.add_header('User-Agent', self.user_agent)
            page = urllib2.urlopen(req).read()
            while '"product_list"' in page:
                request = scrapy.Request(products_url, callback=self.parse)
                list_urls.append(products_url)
                requests.append(request)
                skip += 60
                products_url = url1 + url2 + tab + url3 + str(skip) + url4
                req = urllib2.Request(products_url)
                req.add_header('User-Agent', self.user_agent)
                page = urllib2.urlopen(req).read()
        else:
            flag = self.start_urls[0].find('?')
            if flag != -1:
                flag = self.start_urls[0].find('skip=')
                flag2 = self.start_urls[0].find('&', flag + 1)
                url1 = self.start_urls[0][:flag + 5]
                url2 = self.start_urls[0][flag2:]
                skip = 0
                products_url = url1 + str(skip) + url2
                req = urllib2.Request(products_url)
                req.add_header('User-Agent', self.user_agent)
                page = urllib2.urlopen(req).read()
                while '"product_list"' in page:
                    request = scrapy.Request(products_url, callback=self.parse)
                    list_urls.append(products_url)
                    requests.append(request)
                    skip += 60
                    products_url = url1 + str(skip) + url2
                    req = urllib2.Request(products_url)
                    req.add_header('User-Agent', self.user_agent)
                    page = urllib2.urlopen(req).read()
            else:
                flag = self.start_urls[0].rfind('/', 0, -1)
                tab = self.start_urls[0][flag + 1:]
                skip = 60
                url1 = '?categories%5B%5D='
                url2 = '&sort_field=pv_insert_time&q=&limit=60&skip='
                url3 = '&partner='
                products_url = self.start_urls[0] + url1 + tab + url2 + str(skip) + url3
                req = urllib2.Request(products_url)
                req.add_header('User-Agent', self.user_agent)
                page = urllib2.urlopen(req).read()
                while '"product_list"' in page:
                    request = scrapy.Request(products_url, callback=self.parse)
                    list_urls.append(products_url)
                    requests.append(request)
                    skip += 60
                    products_url = self.start_urls[0] + url1 + tab + url2 + str(skip) + url3
                    req = urllib2.Request(products_url)
                    req.add_header('User-Agent', self.user_agent)
                    page = urllib2.urlopen(req).read()

        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_sku(self, sel, item):
        flag = sel.response.body.find('funnely_product_id = ')
        flag_end = sel.response.body.find(';', flag + 1)
        if (flag != -1) & (flag_end != -1):
            item['sku'] = sel.response.body[flag + len('funnely_product_id = '):flag_end]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'italist'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@class="product_brand"]/a/h1/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_title(self, sel, item):
        title_xpath = '//div[@id="product_title" and @itemprop="name"]/span[@class="bright"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_colors(self, sel, item):
        color_xpath = '//span[@class="selected_option_color pull-left"]/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            data = data[0].strip()
            colors = []
            if len(data) != 0:
                colors.append(data)
                item['colors'] = colors

    def _extract_sizes(self, sel, item):
        size_xpath = '//ul[@id="sizes_cnt"]//span[@class="product_size_size"]/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            sizes = []
            for size in data:
                size = size.strip()
                if len(size) != 0:
                    sizes.append(size)
            if len(size) != 0:
                item['sizes'] = sizes

    def _extract_price(self, sel, item):
        price_xpath = '//div[@id="product_price"]/span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][1:].strip()
            item['price'] = self._format_price('EUR', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@id="product_price"]/span[@class="text_line_through bright"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0][1:].strip()
            item['list_price'] = self._format_price('EUR', list_price_number)

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@id="product_images_thumbs"]/a//@href'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data



def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
