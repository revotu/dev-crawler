# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline
import json
import re

import urllib2

from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'saksoff5th'

class Saksoff5thSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["saksoff5th.com"]

    def __init__(self, *args, **kwargs):
        super(Saksoff5thSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if idx1 != -1:
            return url[:idx1]
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        total_item_xpath = '//div[@class="results-hits"]/text()'
        category_url = sel.response.url
        data = sel.xpath(total_item_xpath).extract()
        if len(data) != 0:
            total_items = (
                re.search(re.compile(r'\d+'), data[0].replace(',', '')).group())
            content = ''
            start = 0
            while start < int(total_items):
                item_url = (category_url + \
                    '?start=%d&format=page-element'
                    '&sz=15&source=lazyload' % start)
                request = urllib2.Request(item_url)
                response = urllib2.urlopen(request)
                content += response.read()
                start += 15
            sel = Selector(text=content)
        base_url = ''
        items_xpath = '//a[@class="name-link"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="pdt-short-desc'
            ' o5-product-short-decription"]/span/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Saksoff5th'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = (
            '//h1[@class="product-name o5-product-name"]/a/span/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@itemprop="productID"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@itemprop="description"]/ul'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        rp_url = sel.response.url
        rp_url = rp_url.replace('/', '.')
        line = rp_url.split('.')
        mid_url = line[6]
        pri_url = 'http://image.s5a.com/is/image/saksoff5th/'
        last_url = '?scl=1&rect=500,0,1000,2000&fmt=jpg'
        imgs = []
        success = True
        for char in mid_url:
            if char < '0' or char > '9':
                success = False
                break
        if success:
            imgs.append(pri_url + mid_url + last_url)
            item['image_urls'] = imgs
        else:
            item['image_urls'] = []

    def _extract_colors(self, sel, item):
        color_xpath = '//li[@class="emptyswatch selectable hidden"]/a/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            content = []
            for line in data:
                if len(line.strip()) != 0:
                    content.append(line.strip())
            item['colors'] = content

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//li[@class="emptyswatch selectable "]/a[1]/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            content = []
            for line in data:
                if len(line.strip()) != 0:
                    content.append(line.strip())
            item['sizes'] = content

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@class="price-sales o5-price-sales"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="o5-price-standard"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_num = data[0][1:].strip()
            item['list_price'] = self._format_price('USD', price_num)

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
        id_xpath = '//span[@itemprop="productID"]/text()'
        data = sel.xpath(id_xpath).extract()
        id = ''
        if len(data) == 0:
            return []
        id = data[0]
        review_url0 = ('http://api.bazaarvoice.com/data/batch.json?' +
                       'passkey=hyrbxxgywpgc1bxezbtcz8qyl&apiversion=5.4' +
                       '&displaycode=16218-en_us&resource.q0=products&' +
                       'filter.q0=id%3Aeq%3Aidnum&stats.q0=reviews&filteredstats.q0=reviews' +
                       '&filter_reviews.q0=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q0=contentlocale' +
                       '%3Aeq%3Aen_US&resource.q1=reviews&filter.q1=isratingsonly' +
                       '%3Aeq%3Afalse&filter.q1=productid%3Aeq%3Aidnum&' +
                       'filter.q1=contentlocale%3Aeq%3Aen_US&sort.q1=relevancy%3Aa1' +
                       '&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors' +
                       '%2Cproducts%2Ccomments&filter_reviews.q1=contentlocale%3Aeq%3Aen_US' +
                       '&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen_US&' +
                       'filter_comments.q1=contentlocale%3Aeq%3Aen_US&limit.q1=')
        review_url0 = review_url0.replace('idnum', id)
        review_url = review_url0 + str(8) + '&offset.q1=0'
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('{')
        indx2 = content.rfind('}')
        content = content[indx1:indx2 + 1]
        review_dict = json.loads(content)
        review_q1 = review_dict['BatchedResults']['q1']
        review_includes = review_q1['Includes']
        review_count = 0
        if ('Products' in review_includes.keys()):
            if(id in review_includes['Products'].keys()):
                review_count = int(review_includes['Products'][id]['ReviewStatistics']['TotalReviewCount'])
            else:
                item['review_count'] = 0
                return []
        else:
            item['review_count'] = 0
            return []
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        item['review_rating'] = float(review_includes['Products'][id]['ReviewStatistics']['AverageOverallRating'])
        review_countRatingsOnly = int(review_includes['Products'][id]['ReviewStatistics']['RatingsOnlyReviewCount'])
        if(review_count <= review_countRatingsOnly):
            return []
        review_url = review_url0 + str(review_count) + '&offset.q1=0'
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('{')
        indx2 = content.rfind('}')
        content = content[indx1:indx2 + 1]
        review_dict = json.loads(content)
        review_q1 = review_dict['BatchedResults']['q1']
        review_results = review_q1['Results']
        review_list = []
        for idx in range(len(review_results)):
            rating = float(review_results[idx]['Rating'])
            date = review_results[idx]['SubmissionTime']
            name = review_results[idx]['UserNickname']
            title = review_results[idx]['Title']
            contents = review_results[idx]['ReviewText']
            review_list.append({'rating':rating,
              'date':date,
              'name':name,
              'title':title,
              'content':contents})
        item['review_list'] = review_list


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
