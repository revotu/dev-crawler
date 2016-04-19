# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline

import urllib2

import re

from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'julesb'

class JulesbSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["julesb.com"]

    def __init__(self, *args, **kwargs):
        self.header = {'Cookie' : 'VSCategoryGroup=2; _gat=1; flxpxlPv_655511=30|0; vscommerce=ru9c06ieee0ersko9krb5soo70; _ga=GA1.2.2046402472.1434336762'}
        super(JulesbSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx = url.find('#')
        self.paras = []
        if idx == -1:
            idx1 = url.find('com/')
            self.base_url = url[idx1 + len('com/'):]
            para_url = url
            cate_url = url
        else:
            idx1 = url.find('com/')
            self.base_url = url[idx1 + len('com/'):idx]
            para_url = 'http://www.julesb.com/' + self.base_url
            self.paras = re.findall(re.compile('[a-z]{1}\d+'), url[idx + 1:])
            cate_url = url[:idx]
        request = urllib2.Request(para_url, headers=self.header)
        response = urllib2.urlopen(request)
        sel = Selector(text=response.read())
        para_xpath = '//fieldset//input[@name="child_categories[]"]/@value'
        self.paras += sel.xpath(para_xpath).extract()
        keyword_xpath = '//fieldset//input[@name="keywords"]/@value'
        data = sel.xpath(keyword_xpath).extract()
        if len(data) != 0:
            self.keywords = data[0]
        else:
            self.keywords = ''
        return cate_url

    def find_items_from_list_page(self, sel, item_urls):
        category_url = ('http://www.julesb.com/ajax/getProductListings'
                '?base_url=%s&page_type=productlistings'
                '&page_variant=show&' % self.base_url)
        for para in self.paras:
            if para[:1] == 'c':
                category_url += 'categories_id[]=' + para[1:] + '&'
            elif para[:1] == 'm':
                category_url += 'manufacturer_id[]=' + para[1:] + '&'
            elif para[:1] == 't':
                category_url += 'tags_id[]=' + para[1:] + '&'
            else:
                category_url += 'categories_id[]=' + para + '&'
        if len(self.keywords) != 0:
            category_url += 'keywords=' + self.keywords + '&'
        category_url += 'all_upcoming_flag[]=78&show=&sort=&page='

        page_num = 1
        requests = []
        while True:
            page_url = category_url + str(page_num)
            request = urllib2.Request(page_url, headers=self.header)
            response = urllib2.urlopen(request)
            content = self._remove_escape(response.read())
            sel = Selector(text=content)
            items_xpath = '//a[@class="product_title"]/@href'
            data = sel.xpath(items_xpath).extract()
            for item_url in data:
                item_url = item_url.replace('[', '%5B').replace(']', '%5D')
                requests.append(scrapy.Request(item_url, \
                    callback=self.parse_item))
                item_urls.append(item_url)
            if data == None or len(data) == 0:
                break
            page_num += 1
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="product_title"]/product_title/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Julesb'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@id="product_page_right_logo"]/a/@alt'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        data = re.search(re.compile('p\d+'), sel.response.url)
        if data != None:
            item['sku'] = data.group()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="product_page_tab_content_cms"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        image_xpath = '//li/a[@id="product_zoom_image"]/@href'
        image1_xpath = '//div[@id="thumb_container"]/ul/li//a/@href'
        data = sel.xpath(image_xpath).extract()
        data1 = sel.xpath(image1_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data
        elif len(data1) != 0:
            item['image_urls'] = data1

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@id="product_price_sale"]'
            '//span[@class="USD"]/@content')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//span[@id="product_price_was"]'
            '/span[@class="price"]/span/span[@class="USD"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()[len('$'):]
            item['list_price'] = self._format_price('USD', list_price_number)

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
