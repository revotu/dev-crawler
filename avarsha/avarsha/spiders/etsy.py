# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline
import urllib2
import re
import json

from avarsha_spider import AvarshaSpider
from scrapy.selector import Selector
from openpyxl import load_workbook

_spider_name = 'etsy'

class EtsySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["etsy.com"]
    brand_list = {}

    def __init__(self, *args, **kwargs):
        super(EtsySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        return []

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        return
        title_xpath = '//*[@itemprop="name"]/text()'
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
        item = {}
        
        location_xpath = '//span[@data-key="user_location"]/text()'
        data = sel.xpath(location_xpath).extract()
        if len(data) != 0:
            item['location'] = data[0].strip()
        else:
            item['location'] = ''
            
        sales_xpath = '//span[@class="shop-sales hide-border no-wrap"]/a/text()'
        data = sel.xpath(sales_xpath).extract()
        if len(data) != 0:
            item['sales'] = data[0].strip().replace(' Sales','')
        else:
            item['sales'] = ''
            
        since_xpath = '//span[@class="etsy-since no-wrap"]/text()'
        data = sel.xpath(since_xpath).extract()
        if len(data) != 0:
            item['since'] = data[0].strip()
        else:
            item['since'] = ''
            
        rating_xpath = '//span[@class="total-rating-count text-gray-lighter ml-xs-1"]/text()'
        data = sel.xpath(rating_xpath).extract()
        if len(data) != 0:
            item['rating'] = data[0].strip().replace('(','').replace(')','')
        else:
            item['rating'] = ''
            
        favorers_reg = re.compile(r'"num_favorers":(\d+?),')
        data = favorers_reg.findall(sel.response.body)
        if len(data) != 0:
            item['favorers'] = data[0].strip()
        else:
            item['favorers'] = ''

        announcement_xpath = '//p[@class="text-gray-lighter announcement-collapse"]/span[@data-key="message"]/text()'
        data = sel.xpath(announcement_xpath).extract()
        if len(data) != 0:
            item['announcement'] = ''.join(data).replace('\r\n',' ')
        else:
            item['announcement'] = ''
        
        items_name_xpath = '//div[@class="dropdown is-closed dropdown-bottom-left"]/div/ul/li/a/text()'
        data_name = sel.xpath(items_name_xpath).extract()
        items_number_xpath = '//div[@class="dropdown is-closed dropdown-bottom-left"]/div/ul/li/a/span/text()'
        data_number = sel.xpath(items_number_xpath).extract()
        if len(data_name) != 0 and len(data_number) != 0:
            data_name = [name.strip() for index,name in enumerate(data_name) if index%2 == 0]
            item['items'] = json.dumps(dict(zip(data_name,data_number)), ensure_ascii=False)
        else:
            item['items'] = ''
        #print item
        
        
        wb = load_workbook('shop.xlsx')
        ws = wb.active
        brand_row = sel.response.url[sel.response.url.find('?row=') + len('?row='):]
        ws.cell(row = brand_row, column =3).value = item['location']
        ws.cell(row = brand_row, column =4).value = item['sales']
        ws.cell(row = brand_row, column =5).value = item['since']
        ws.cell(row = brand_row, column =6).value = item['rating']
        ws.cell(row = brand_row, column =7).value = item['favorers']
        ws.cell(row = brand_row, column =8).value = item['announcement']
        ws.cell(row = brand_row, column =9).value = item['items']
        wb.save('shop.xlsx')

    def _extract_description(self, sel, item):
        return
        desc_xpath = '//*[@id="description-text"]'
        data = sel.xpath(desc_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        return
        imgs_xpath = '//*[@id="image-carousel"]/li/@data-full-image-href'
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
        return
        price_xpath = '//*[@property="etsymarketplace:price_value"]/@content'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            item['price'] = self._format_price('USD', price_number)

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
