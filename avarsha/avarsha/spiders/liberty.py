# -*- coding: utf-8 -*-
# author: huoda
import re

import json
import time
from time import *
import urllib2, cookielib
import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'liberty'

class LibertySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["liberty.co.uk"]

    def __init__(self, *args, **kwargs):
        super(LibertySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.liberty.co.uk/'
        items_xpath = '//*[@class="img_link"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def _find_items_from_list_page(self, sel, base_url, items_xpath, item_urls):
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_url = item_url.replace('\n', '%0A')
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.liberty.co.uk'
        nexts_xpath = '//*[@class="page-next"][1]//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_url = list_url.replace(' ', '%20')
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url
#         item['url'] = item['url'].replace('%0A', '\n')

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="product_title"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'liberty'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@id="product_brand"]/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//@data-product-id'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="accordionActive"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        img_xpath = '//*[@id="alternative_images"]//img//@src'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            imgs = []
            for img in data:
                img = img.replace('thumbnail', 'enlarge')
                imgs.append(img)
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_xpath = '//*[@id="product_size"]/*[@class="size"]//text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            sizes = []
            for size in data:
                size = size.strip()
                if len(size) != 0:
                    sizes.append(size)
            if len(sizes) != 0:
                item['sizes'] = sizes

    def _extract_price(self, sel, item):
        price_xpath = '//*[@class="product_price"]/span[@class="now"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            data[0] = data[0].strip()
            price_number = data[0][4:].strip()
            item['price'] = self._format_price('GBP', price_number)
        else:
            price_xpath = '//*[@class="product_price"]/span/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                data[0] = data[0].strip()
                price_number = data[0][1:].strip()
                item['price'] = self._format_price('GBP', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@class="product_price"]/span[@class="was"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data[0] = data[0].strip()
            list_price_number = data[0][4:].strip()
            item['list_price'] = self._format_price('GBP', list_price_number)



    def _extract_review_list(self, sel, item):
        content = sel.response.body
        indx1 = content.find("itemId:")
        indx2 = content.find('"', indx1 + len("itemId:")) + len('"')
        indx3 = content.find('"', indx2)
        id = ''
        if indx1 != -1:
            id = content[indx2:indx3]
        else:
            item['review_count'] = 0
            return []
        head_url = 'http://www.liberty.co.uk/ratings/reviews/retailer/ref/UATLiberty/item/idnum?page='
        tail_url = '&results=9999&orderby=submittedDate&sortby=DESC&language=&gradings=10&callback=review'
        head_url = head_url.replace('idnum', id)
        review_url = head_url + str(1) + tail_url
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('(') + len('(')
        indx2 = content.rfind(')')
        content = content[indx1:indx2]
        review_dict = json.loads(content)
        if(review_dict['summary'] == None):
            item['review_count'] = 0
            return []
        review_count = review_dict['summary']['numberOfRatings']
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        item['review_rating'] = float(review_dict['summary']['averageRating']) / 100.0 * 5.0
        pagenum = 1;
        review_content = review_dict['content']
        review_list = []
        while len(review_content) != 0:
            for i in range(len(review_content)):
                rating = float(review_content[i]["rating"]) / 100.0 * 5.0
                sec = float(review_content[i]["submittedDate"]) / 1000.0
                date = self.secs2str(sec)
                name = review_content[i]["reviewer"]["screenName"]
                if len(name) == 0:
                    name = review_content[i]["reviewer"]["firstName"] + ' ' + review_content[i]["reviewer"]["lastName"]
                title = ''
                conts = review_content[i]["comments"]
                review_list.append({'rating':rating,
                  'date':date,
                  'name':name,
                  'title':title,
                  'content':conts})
            pagenum += 1
            review_url = head_url + str(pagenum) + tail_url
            request = urllib2.Request(review_url)
            response = urllib2.urlopen(request)
            content = response.read()
            indx1 = content.find('(') + len('(')
            indx2 = content.rfind(')')
            content = content[indx1:indx2]
            review_dict = json.loads(content)
            review_content = review_dict['content']
        item['review_list'] = review_list

    def secs2str(self, secs):
        return strftime("%Y-%m-%d %H:%M:%S", localtime(secs))
def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
