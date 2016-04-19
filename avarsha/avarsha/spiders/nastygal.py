# -*- coding: utf-8 -*-
# author: tanyafeng

import re
import json
import scrapy.cmdline
import urllib2
from avarsha_spider import AvarshaSpider


_spider_name = 'nastygal'

class NastygalSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["nastygal.com"]

    def __init__(self, *args, **kwargs):
        super(NastygalSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        requests = []
        item_pattern = re.compile('href="(.*?)"')
        for line in sel.response.body.split('\n'):
            if line.find('class="product-link"') != -1:
                match = item_pattern.findall(line)
                item_urls.append(match[0])
                requests.append(scrapy.Request(match[0], \
                    callback=self.parse_item))

        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.nastygal.com/'
        nexts_xpath = ('//*[@class=\'pagination-wrapper clearfix\']//a'
            '[@class=\'js-ajax next\']/@href')

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@property=\'og:title\']/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Nastygal'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Nastygal'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*/div/@data-style-id'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="product-description"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        base_url = 'http:'
        img_xpath = '//*[@class=\'product-image\']/@src'
        data = sel.xpath(img_xpath).extract()
        for img_url in data:
            imgs.append(base_url + img_url)
        if len(imgs) != 0:
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//*[@property=\'og:color\']/@content'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//*[@class="sku-label"]/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        currency_xpath = '//*[@property=\'og:price:currency\']/@content'
        price_xpath = '//*[@property=\'og:price:amount\']/@content'
        price_str = sel.xpath(price_xpath).extract()
        currency_str = sel.xpath(currency_xpath).extract()
        if len(currency_str) != 0 and len(price_str) != 0:
            item['price'] = self._format_price(currency_str[0], price_str[0])

    def _extract_list_price(self, sel, item):
        currency_xpath = '//*[@property=\'og:price:currency\']/@content'
        price_xpath = '//*[@property=\'og:price:standard_amount\']/@content'
        price_str = sel.xpath(price_xpath).extract()
        currency_str = sel.xpath(currency_xpath).extract()
        if len(currency_str) != 0 and len(price_str) != 0:
            item['list_price'] = self._format_price(currency_str[0], \
                                                    price_str[0])

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
        productid_xpath = '//input[@name="ProductId"]/@value'
        data = sel.xpath(productid_xpath).extract()
        if len(data) == 0:
            return []
        id = data[0]
        review_count_xpath = '//div[@class="product-rating"]//span[@class="rating-count"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if(len(data) == 0):
            item['review_count'] = 0
            return []
        review_count = int(data[0])
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        review_rating_xpath = '//div[@class="product-rating"]/meta[@itemprop="ratingValue"]/@content'
        data = sel.xpath(review_rating_xpath).extract()
        item['review_rating'] = float(data[0])
        review_url = ('http://www.nastygal.com/bv/reviews?Filter=' +
                    'Productid:idnum&Limit=limitnum&Sort=SubmissionTime:desc' +
                    '&Include=Products&Stats=Reviews&instart_disable_injection=true')
        review_url = review_url.replace('idnum', id).replace('limitnum', str(review_count))
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        review_dict = json.loads(content)
        review_results = review_dict["Results"]
        review_list = []
        for idx in range(len(review_results)):
            rating = float(review_results[idx]["Rating"])
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
