# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline
import math
from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider
import re
import urllib2

_spider_name = "apeainthepod"

class ApeainthepodSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["apeainthepod.com"]

    def __init__(self, *args, **kwargs):
        super(ApeainthepodSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//span[@class="thumbback"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//a[@class="pageselectorlink"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Apeainthepod'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Apeainthepod'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="PidNum"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            index = data[0].find(':')
            item['sku'] = data[0][index + 1:].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_url_list = []
        small_img_xpath = ('//img[@class="clams"]/@src')
        small_img_url_list = sel.xpath(small_img_xpath).extract()
        for small_img_url in small_img_url_list:
            img_mark = (small_img_url[small_img_url.find('[')
                + 1:small_img_url.find(']')])
            big_img_url = ('http://img.destinationmaternity.com/products/%s'
                % img_mark)
            img_url_list.append(big_img_url)
        item['image_urls'] = img_url_list

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            idx = data[0].find('$')
            price_number = data[0][idx + 1:].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="pricestrike"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            idx = data[0].find('$')
            list_price_number = data[0][idx + 1:].strip()
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
        id_xpath = '//div[@class="PidNum"]/text()'
        data = sel.xpath(id_xpath).extract()
        id = ''

        if len(data) != 0:
            data[0] = data[0].replace(' ', '')
            indx = data[0].find('#:') + len('#:')
            id = data[0][indx:]
        review_url = 'http://reviews.apeainthepod.com/0567p/idnum/reviews.htm?format=embedded'
        review_url = review_url.replace('idnum', id)
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('BVRRNumber BVRRBuyAgainTotal')
        if indx1 == -1:
            item['review_count'] = 0
            return []
        indx2 = content.find('>', indx1) + len('>')
        indx3 = content.find('<', indx2)
        data = content[indx2:indx3]
        review_count = 0
        if len(data) != 0:
            review_count = int(data)
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        indx1 = content.find('BVImgOrSprite')
        indx2 = content.find('alt=', indx1) + len('alt=')
        indx2 = content.find('"', indx2) + len('"')
        indx3 = content.find('out', indx2)
        data = content[indx2:indx3]
        if len(data) != 0:
            item['review_rating'] = float(data)
        review_num = 0;
        review_url0 = review_url
        pageidx = 0
        review_list = []
        while review_num < review_count:
            pageidx += 1
            pagenum = str(pageidx)
            review_url = review_url0 + '&page=' + pagenum + '&scrollToTop=true'
            request = urllib2.Request(review_url)
            response = urllib2.urlopen(request)
            content = []
            content = response.read()
            indx = content.find('BVSubmissionPopupContainer')
            while indx != -1:
                indx += len('BVSubmissionPopupContainer')
                indx1 = content.find('BVRRNumber BVRRRatingNumber', indx) + len('BVRRNumber BVRRRatingNumber')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                data = content[indx2:indx3]
                rating = float(data)
                indx1 = content.find('BVRRValue BVRRReviewDate', indx) + len('BVRRValue BVRRReviewDate')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                date = content[indx2:indx3]
                indx1 = content.find('BVRRNickname', indx) + len('BVRRNickname')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                name = content[indx2:indx3]
                indx1 = content.find('BVRRValue BVRRReviewTitle', indx) + len('BVRRValue BVRRReviewTitle')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                title = content[indx2:indx3]
                indx1 = content.find('span class="BVRRReviewText"', indx) + len('span class="BVRRReviewText"')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('span', indx2)
                cont = content[indx2:indx3 - 2]
                review_list.append({'rating':rating,
                  'date':date,
                  'name':name,
                  'title':title,
                  'content':cont})
                indx = content.find('BVSubmissionPopupContainer', indx)
                review_num += 1
        item['review_list'] = review_list


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
