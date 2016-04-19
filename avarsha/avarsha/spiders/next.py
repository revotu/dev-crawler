# -*- coding: utf-8 -*-
# @author: zhangliangliang

import re
import json
import scrapy.cmdline
import urllib2
from avarsha_spider import AvarshaSpider

_spider_name = "next"

class NextSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["next.co.uk"]

    def __init__(self, *args, **kwargs):
        super(NextSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if idx1 != -1:
            return url[:idx1]
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.next.co.uk'
        items_xpath = '//h2[@class="Title"]/a/@href'
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            idx1 = path.find('#')
            if idx1 != -1:
                item_url = path[:idx1]
            else:
                item_url = path
            item_urls.append(base_url + item_url)
            request = scrapy.Request(base_url + item_url, \
                callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = ('//div[@class="ResultsFooter TopShadow"]'
            '/div[@class="Pages"]//a/@href')

        # don't need to change this line
        requests = self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)
        i = 0
        while i < len(list_urls):
            list_urls[i] = self._url_quote(list_urls[i])
            i += 1
        return requests

    def merge(self, sel, des_xpath, data):
        if len(data) != 0:
            data.append(' '.join(sel.xpath(des_xpath).extract()))
        else:
            data = sel.xpath(des_xpath).extract()

        return data

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = (
            '//div[@class="StyleHeader"]/div[@class="Title"]/h1/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Next.co'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Next.co'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="ItemNumber"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="StyleContent "]'
        sel1 = sel.xpath(description_xpath)
        description_xpath = 'div[1]/span[@class="tov"]/text()'
        data = sel1.xpath(description_xpath).extract()
        description_xpath = 'div[1]/text()'
        data = self.merge(sel1, description_xpath, data)
        description_xpath = 'div[2]/text()'
        data = self.merge(sel1, description_xpath, data)
        description_xpath = 'div[3]//div[@class="description"]/text()'
        data = self.merge(sel1, description_xpath, data)
        if len(data) != 0:
            ans = ''
            for line in data:
                ans += line
            item['description'] = ans.strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        image_url_xpath = '//div[@class="itemsContainer"]//a//@rel'
        data = sel.xpath(image_url_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        colors_xpath = '//select[@name="Colour"]//option/text()'
        data = sel.xpath(colors_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        sizes_xpath = '//select[@name="Size"]//option/text()'
        data = sel.xpath(sizes_xpath).extract()
        if len(data) >= 1:
            idx = 1
            while idx < len(data):
                if data[idx] == 'Choose Size':
                    break
                idx += 1
            if idx >= len(data):
                item['sizes'] = data[1:]
            else:
                item['sizes'] = data[1:idx]


    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//section[@class="StyleCopy"]/div[1]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_num = str(re.search(re.compile('\d+'), data[0]).group())
            item['price'] = self._format_price("GBP ", price_num)

    def _extract_list_price(self, sel, item):
        pass

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
        productid_xpath = '//input[@id="idList"]/@value'
        data = sel.xpath(productid_xpath).extract()
        print data
        if len(data) == 0:
            return []
        indx = data[0].find(',')
        id = ''
        if indx != -1:
            id = data[0][:indx]
        else:
            id = data[0]
        review_url = ('http://next.ugc.bazaarvoice.com/data/' +
        'reviews.json?apiversion=5.3&passkey=2l72hgc4hdkhcc1bqwyj1dt6d' +
        '&sort=SubmissionTime:desc&Limit=1&Filter=ProductId:idnum&Offset=0' +
        '&Include=Comments,Products&Stats=Reviews&callback=bvLoadReviewCallback')
        review_url = review_url.replace('idnum', id)
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('(') + len('(')
        indx2 = content.rfind(')')
        content = content[indx1:indx2]
        review_dict = json.loads(content)
        review_count = int(review_dict["TotalResults"])
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        print review_url
        print review_dict["Includes"]
        item['review_rating'] = float(review_dict["Includes"]["Products"][id]["ReviewStatistics"]["AverageOverallRating"])
        review_url = review_url.replace('Limit=1', 'Limit=' + str(review_count)).replace(',Products&Stats=Reviews', '')
        review_url = review_url.replace('idnum', id)
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('(') + len('(')
        indx2 = content.rfind(')')
        content = content[indx1:indx2]
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
