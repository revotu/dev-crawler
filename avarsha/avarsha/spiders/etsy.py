# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline
import urllib2
import re
import json

from w3lib.html import remove_tags
from avarsha_spider import AvarshaSpider
from scrapy.selector import Selector
from openpyxl import load_workbook

_spider_name = 'etsy'

class EtsySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["etsy.com"]

    def __init__(self, *args, **kwargs):
        super(EtsySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        
        base_url = ''
        items_xpath = '//div[@class="block-grid-item listing-card position-relative parent-hover-show"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="pagination btn-group clearfix mt-xs-3"]/a[last()]/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Etsy'

    def _extract_brand_name(self, sel, item):
        return

    def _extract_sku(self, sel, item):
        return
        sku_xpath = '//*[@data-convo_source="listing_convo"]/@data-referring_id'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        return

    def _extract_description(self, sel, item):
        desc_xpath = '//div[@id="item-overview"]/ul/li/node()'
        data = sel.xpath(desc_xpath).extract()
        if len(data) != 0:
            data = [remove_tags(v.strip()) for v in data]
            description = ';'.join(data).replace(':;',':').replace('from;','from ')
            item['description'] = description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//ul[@id="image-carousel"]/li/@data-full-image-href'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//meta[@property="etsymarketplace:price_value"]/@content'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = data[0].strip()

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
        return
        count_xpath = '//span[@class="review-rating"]//meta[@itemprop="count"]/@content'
        data = sel.xpath(count_xpath).extract()
        review_count = 0
        if len(data) == 0:
            item['review_count'] = 0
            return []
        else:
            review_count = int(data[0])
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        rating_xpath = '//span[@class="review-rating"]//meta[@itemprop="rating"]/@content'
        data = sel.xpath(rating_xpath).extract()
        review_rating = 5.0
        if len(data) != 0:
            review_rating = float(data[0])
        item['review_rating'] = review_rating
        review_url0_xpath = '//a[@data-target-id="reviews"]/@href'
        review_url0 = sel.xpath(review_url0_xpath).extract()
        if len(review_url0) == -1:
            return []
        content = ''
        pagenum = 1
        review_url = 'https://www.etsy.com' + review_url0[0] + '?page=1'
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        ratings = []
        dates = []
        names = []
        titles = []
        conts = []
        review_list = []
        r_l = []
        while 'receipt-review' in content:
            sel = Selector(text=content)
            review_rating_xpath = '//ul[@class="receipt-review"]//input[@name="rating"]/@value'
            review_date_xpath = '//ul[@class="receipt-review"]/li[@class="reviewer-info"]/span[2]/text()'
            review_name_xpath = '//ul[@class="receipt-review"]/li[@class="reviewer-info"]/span[1]/a/text()'
            review_title_xpath = '//ul[@class="receipt-review"]//div[@class="review-container clear"]//h2[@class="transaction-title"]/a/text()'
            review_content_xpath = '//ul[@class="receipt-review"]//div[@class="review-container clear"]//p[@class="review"]/text()'
            review_rating = sel.xpath(review_rating_xpath).extract()
            review_date = sel.xpath(review_date_xpath).extract()
            review_name = sel.xpath(review_name_xpath).extract()
            review_title = sel.xpath(review_title_xpath).extract()
            review_content = sel.xpath(review_content_xpath).extract()
            review_num = min(len(review_rating), len(review_date), len(review_name), len(review_title), len(review_content))
            if review_num != 0:
                for i in range(review_num):
                    ratings.append(float(review_rating[i]))
                    review_date[i] = review_date[i].replace('on ', '')
                    dates.append(review_date[i])
                    names.append(review_name[i])
                    idx1 = review_title[i].find('\n')
                    idx2 = len(review_title[i]) - 1
                    if idx1 != -1 and idx1 < len('\n'):
                        idx1 += len('\n')
                        while review_title[i][idx1] == ' ' and idx1 <= idx2:
                            idx1 += 1
                        while review_title[i][idx2] == ' ':
                            idx2 -= 1
                        review_title[i] = review_title[i][idx1:idx2].replace('\n', '')
                        titles.append(review_title[i])
                    else:
                        titles.append(review_title[i])
                    idx1 = review_content[i].find('\n')
                    idx2 = len(review_content[i]) - 1
                    if idx1 != -1 and idx1 < len('\n'):
                        idx1 += len('\n')
                        while review_content[i][idx1] == ' ' and idx1 <= idx2:
                            idx1 += 1
                        while review_content[i][idx2] == ' ':
                            idx2 -= 1
                        review_content[i] = review_content[i][idx1:idx2].replace('\n', '')
                        conts.append(review_content[i])
                    else:
                        conts.append(review_content[i])
            for j in range(review_num):
                review_list.append({'rating':ratings[j],
                                  'date':dates[j],
                                  'name':names[j],
                                  'title':titles[j],
                                  'content':conts[j]})
            pagenum += 1
            review_url = 'https://www.etsy.com' + review_url0[0] + '?page=' + str(pagenum)
            request = urllib2.Request(review_url)
            response = urllib2.urlopen(request)
            content = response.read()
            ratings = []
            dates = []
            names = []
            titles = []
            conts = []
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
