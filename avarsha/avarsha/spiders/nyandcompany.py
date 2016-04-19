# -*- coding: utf-8 -*-
# @author: donglongtu

import re
import urllib2
import json
import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'nyandcompany'

class NyandcompanySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["nyandcompany.com"]

    def __init__(self, *args, **kwargs):
        super(NyandcompanySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.nyandcompany.com'
        items_xpath = '//*[@class="name"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.nyandcompany.com'
        nexts_xpath = '//*[@class="nav"]/a[@class="next"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="mimic_cart"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Nyandcompany'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@id="brandName"]/@value'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="meta sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="content1 details displayBlock"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_set_url = ('http://images.nyandcompany.com/is/image/NewYorkComp'
            'any/%s_is?req=set,json,UTF-8' % item['sku'])
        response = urllib2.urlopen(imgs_set_url).read()
        imgs_set_reg = re.compile(r'NewYorkCompany/(.+?)"')
        data = imgs_set_reg.findall(response)
        imgs_set = list(set(data))
        for img in imgs_set:
            if img.find('_is') == -1:
                imgs.append('http://images.nyandcompany.com/is/image/NewYork'
                    'Company/%s?&wid=1200&hei=1200&fmt=jpg' % img)
        if len(imgs) == 0:
            imgs.append('http://images.nyandcompany.com/is/image/NewYork'
                'Company/%s?&wid=1200&hei=1200&fmt=jpg' % item['sku'])
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@id="productPrice"]/span[@class="saleprice"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[len(data) - 1].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)
        else :
            price_xpath = '//*[@id="productPrice"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[(len(data) - 1) / 2].strip()[len('$'):]
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@id="productPrice"]/span'
            '[@class="regprice"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[len(data) - 1].strip()[len('$'):]
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

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        id_xpath = '//meta[@itemprop="productID"]/@content'
        data = sel.xpath(id_xpath).extract()
        id = ''
        if len(data) == 0:
            return []
        id = data[0]
        review_url0 = ('http://api.bazaarvoice.com/data/batch.json?' +
                       'passkey=2aut1tbo3ryiyudz88oi96ol3&apiversion=5.5' +
                       '&displaycode=3510-en_us&resource.q0=products' +
                       '&filter.q0=id%3Aeq%3Aidnum&stats.q0=reviews' +
                       '&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_US' +
                       '&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US&resource.q1=reviews' +
                       '&filter.q1=isratingsonly%3Aeq%3Afalse&filter.q1=productid%3Aeq%3Aidnum' +
                       '&filter.q1=contentlocale%3Aeq%3Aen_US&sort.q1=submissiontime%3Adesc' +
                       '&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors%2Cproducts%2Ccomments' +
                       '&filter_reviews.q1=contentlocale%3Aeq%3Aen_US' +
                       '&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen_US' +
                       '&filter_comments.q1=contentlocale%3Aeq%3Aen_US&limit.q1=')
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
