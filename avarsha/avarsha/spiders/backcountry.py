# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import json
import scrapy.cmdline
import math
from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider
import re
import urllib2

_spider_name = 'backcountry'

class BackcountrySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["backcountry.com"]

    def __init__(self, *args, **kwargs):
        super(BackcountrySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.backcountry.com'
        items_xpath = '//a[@class="qa-product-link js-product-link"]/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.backcountry.com'
        nexts_xpath = '//div[@class="pag "]/ul//a/@href'
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_url = list_url.replace(' ', '+').replace('[]', '%5B%5D')
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        _title = ''
        title_xpath = '//h1[@class="header-2 product-name qa-product-title"]\
            //text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            for _data in data:
                data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|(?:  )+|(?:amp;)+|\
                    (?:&#39;)+')
                _data = data_re.sub('', _data)
                _title = ''.join([_title, _data])
            item['title'] = _title

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Backcountry'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//span[@class="qa-brand-name"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if(len(data) != 0):
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//b[@itemprop="productID"]/text()'
        _sku = sel.xpath(sku_xpath).extract()
        if(len(_sku) != 0):
            item['sku'] = str(_sku[0])

    def _extract_features(self, sel, item):
        _features = {}
        _name = ''
        _value = ''
        features_xpath = '//div[@class="table"]'
        features = sel.xpath(features_xpath).extract()
        if len(features) != 0:
            line = features[0]
            while(True):
                idx1 = line.find("<em>")
                if(idx1 != -1):
                    idx2 = line.find("</em>", idx1 + len("<em>"))
                    _name = line[idx1 + len("<em>"):idx2]
                    line = line[idx2:]
                else:
                    break
                idx1 = line.find('class="td">')
                if(idx1 != -1):
                    idx2 = line.find('</div>', idx1 + len('class="td">'))
                    _value = line[idx1 + len('class="td">'):idx2]
                    line = line[idx2:]
                _features[_name] = _value
        item['features'] = _features

    def _extract_description(self, sel, item):
        description_details_xpath = '//div[@id="product-information"]'
        data_details = sel.xpath(description_details_xpath).extract()
        _data_details = ''
        if len(data_details) != 0:
            _data_details = data_details[0]
        item['description'] = _data_details

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_url_xpath = \
            '//ul[@id="color-attribute-selector"]//li/@data-large-img'
        imgs_url = sel.xpath(imgs_url_xpath).extract()
        imgs_detail_xpath = \
            '//ul[@id="detail_carousel_list"]//li/@data-large-img'
        imgs_detail = sel.xpath(imgs_detail_xpath).extract()
        if len(imgs_url) != 0:
            for image_url in imgs_url:
                if(image_url.find('http://') == -1):
                    image_url = 'http:'.join(['', image_url])
                imgs.append(image_url)
        if len(imgs_detail) != 0:
            for image_url in imgs_detail:
                if(image_url.find('http://') == -1):
                    image_url = 'http:'.join(['', image_url])
                imgs.append(image_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        price = sel.xpath(price_xpath).extract()
        if len(price) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|(?:amp;)+|\
                (?:&#39;)+|[$]')
            item['price'] = self._format_price('USD', data_re.sub('', price[0]))

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@itemprop="highPrice"]/text()'
        list_price = sel.xpath(list_price_xpath).extract()
        if len(list_price) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|(?:amp;)+|\
                (?:&#39;)+|[$-]')
            item['list_price'] = \
                self._format_price('USD', data_re.sub('', list_price[0]))

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
        review_count_xpath = '//span[@itemprop="reviewCount"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        review_count = 0
        if len(data) != 0:
            review_count = int(data[0])
        item['review_count'] = review_count
        print 'review_count', review_count
        if review_count == 0:
            return []
        review_rating_xpath = '//div[@class="aggregate-rating"]/span[@itemprop="ratingValue"]/text()'
        data = sel.xpath(review_rating_xpath).extract()
        if len(data) != 0:
            item['review_rating'] = float(data[0])
        item['max_review_rating'] = 5
        url = sel.response.url
        indx1 = url.find("skid=") + len("skid=")
        indx2 = url.find("-", indx1)
        id = ''
        if indx2 != -1:
            id = url[indx1:indx2]
        else:
            id = url[indx1:]
        review_url0 = 'http://www.backcountry.com/community/product/idnum/wall?siteId=1&pageSize=20&pageNumber='
        review_url0 = review_url0.replace('idnum', id)
        review_url = review_url0 + '0&contentType=review'
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        review_dict = json.loads(content)
        reviews = review_dict['contents']
        indx = len(reviews)
        review_list = []
        pageNumber = 0
        while indx != 0:
            for idx in range(len(reviews)):
                if ('starRating' in reviews[idx].keys()):
                    data = reviews[idx]['starRating']
                    rating = float(data)
                    date = reviews[idx]['created']
                    name = reviews[idx]['user']['displayName']
                    title = reviews[idx]['title']
                    cont = reviews[idx]['description']
                    review_list.append({'rating':rating,
                      'date':date,
                      'name':name,
                      'title':title,
                      'content':cont})
            pageNumber += 1
            review_url = review_url0 + str(pageNumber) + '&contentType=review'
            content = ''
            request = urllib2.Request(review_url)
            response = urllib2.urlopen(request)
            content = response.read()
            review_dict = json.loads(content)
            reviews = review_dict['contents']
            indx = len(reviews)
        item['review_list'] = review_list



def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
