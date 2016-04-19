# -*- coding: utf-8 -*-
# author: yangxiao

import json
import math
from scrapy.selector import Selector
import urllib2

import re
import scrapy.cmdline
from avarsha_spider import AvarshaSpider


_spider_name = 'brooksbrothers'

class BrooksbrothersSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["brooksbrothers.com"]

    def __init__(self, *args, **kwargs):
        super(BrooksbrothersSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.brooksbrothers.com'
        items_xpath = ('//div[@id="productsearchresult-productgrid"]'
            '//li[@class="grid-tile"]//div[@class="product-name"]/h2'
            '/a[@class="name-link"]/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = ('//div[@class="pgindxcontent-wrapper"]'
            '/a[@class="page-next page-nav-btn"]/@href')

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="product-top-details"]'
            '/h1[@class="product-name"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'brooksbrothers'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'brooksbrothers'

    def _extract_sku(self, sel, item):
        sku_xpath = ('//div[@class="product-top-details"]'
            '//span[@itemprop="productID"]/text()')
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//li[@class="toggle-menu-body"]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//div[@class="product-thumbnails"]'
            '/ul[@class="pdp-thumbnails"]/li/a/@data-alt-img-href')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = list(set(data))
        else:
            other_imgs_xpath = \
                ('//a[@class="product-image main-image cloud-zoom"]/@href')
            data = sel.xpath(other_imgs_xpath).extract()
            if len(data) != 0:
                item['image_urls'] = list(set(data))

    def _extract_colors(self, sel, item):
        selected_color_xpath = ('//h3[@class="ColorSwatchesHeader"]'
            '/span[@class="displayvalue"]/text()')
        colors = sel.xpath(selected_color_xpath).extract()
        if len(colors) != 0:
            colors += re.findall \
                ('emptyswatch.|\n*title="(.*)"\nclass="swatchanchor"', \
                    sel.response.body)
            item['colors'] = list(set(colors))

    def _extract_sizes(self, sel, item):
        size_xpath = ('//div[@class="product-variations"]'
            '//div[@class="chzn-row ie-tweak"]/select/option/text()')
        size_list = sel.xpath(size_xpath).extract()
        if len(size_list) != 0:
            item['sizes'] = \
                map(lambda i:i.replace('\n', ''), size_list)

    def _extract_stocks(self, sel, item):
        pass

    def _extract_prices(self, sel, item):
        self._extract_list_price(sel, item)
        self._extract_price(sel, item)
        self._extract_low_price(sel, item)
        self._extract_high_price(sel, item)

    def _extract_price(self, sel, item):
        price_xpath1 = '//span[@class="priceDisplay"]/span/span[1]/text()'
        price_xpath2 = '//span[@class="priceDisplay"]/span/span[2]/text()'
        price_first_letter = sel.xpath(price_xpath1).extract()
        price = sel.xpath(price_xpath2).extract()
        if len(price_first_letter) != 0 and len(price) != 0:
            price_number = price[0]
            price_first_letter[0] = price_first_letter[0].replace('$', 'USD')
            item['price'] = self._format_price(price_first_letter[0], price_number)


    def _extract_list_price(self, sel, item):
        price_xpath1 = '//span[@class="price-standard discounted"]/span/span[1]/text()'
        price_xpath2 = '//span[@class="price-standard discounted"]/span/span[2]/text()'
        price_first_letter = sel.xpath(price_xpath1).extract()
        price = sel.xpath(price_xpath2).extract()
        if len(price_first_letter) != 0 and len(price) != 0:
            price_number = price[0]
            price_first_letter[0] = price_first_letter[0].replace('$', 'USD')
            item['list_price'] = self._format_price(price_first_letter[0], price_number)

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
        url = sel.response.url
        indx1 = url.rfind("/")
        indx2 = url.find(",", indx1)
        id = ''
        id = url[indx1 + 1:indx2]
        review_url0 = ('http://api.bazaarvoice.com/data/batch.json?passkey=9w2' + \
                     'tym5rfnn1b0ak15h3vtvoa&apiversion=5.5&displaycode=8103-en_us' + \
                     '&resource.q0=products&filter.q0=id%3Aeq%3Aidnum&stats.q0=reviews' + \
                     '&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_US' + \
                     '&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US&resource.q1=reviews&' + \
                     'filter.q1=isratingsonly%3Aeq%3Afalse&filter.q1=productid%3Aeq%3Aidnum&filter.q1=' + \
                     'contentlocale%3Aeq%3Aen_US&sort.q1=submissiontime%3Adesc&stats.q1=reviews&filteredstats.' + \
                     'q1=reviews&include.q1=authors%2Cproducts%2Ccomments&filter_reviews.q1=contentlocale' + \
                     '%3Aeq%3Aen_US&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen_US&filter_comments.q1=' + \
                     'contentlocale%3Aeq%3Aen_US&limit.q1=')
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
