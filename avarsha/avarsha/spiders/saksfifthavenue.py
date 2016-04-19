# -*- coding: utf-8 -*-
# @author: donglongtu

import re
import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'saksfifthavenue'

class SaksfifthavenueSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["saksfifthavenue.com"]

    def __init__(self, *args, **kwargs):
        super(SaksfifthavenueSpider, self).__init__(*args, **kwargs)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            if list_url.find(' ') != -1:
                list_url = list_url.replace(' ', '%20')
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.saksfifthavenue.com'
        items_xpath = '//*[@class="product-text"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.saksfifthavenue.com'
        nexts_xpath = '//*[@class="pa-enh-pagination-right-arrow"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//*[@class="short-description component component-1"]'
            '/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Saksfifthavenue'

    def _extract_brand_name(self, sel, item):
        brand_reg = re.compile(r'"brand":"(.+?)"')
        data = brand_reg.findall(sel.response.body)
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="sku light-text component component-1"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_reg = re.compile(r'\"description\":\"(.+?)\",')
        data = description_reg.findall(sel.response.body)
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        if sel.response.url == 'http://www.saksfifthavenue.com/Entry.jsp':
            return item
        img_url = ('http://image.s5a.com/is/image/saks/' +
            item['sku'] + '_IS?req=imageset')
        img_list = []
        try :
            content = urllib2.urlopen(img_url).read()
            img_url_reg = re.compile('saks/(.+?)(?:;|,)')
            img_url_list = img_url_reg.findall(content)
            img_url_list = list(set(img_url_list))
            for img in img_url_list:
                img_list.append('http://image.s5a.com/is/image/saks/' + img
                    + '_396x528.jpg')
        except Exception as err1:
            self.log('Parse item link: %s' % sel.response.url, err1)
        if len(img_list) > 0:
            item['image_urls'] = img_list

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_reg = re.compile(r'\"sale_price\":\"(.+?)\"')
        price = price_reg.findall(sel.response.body)
        if len(price) != 0:
            data = price[0].strip()
            price_number = data[data.rfind(';') + 1:]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_reg = re.compile(r'\"list_price\":\"(.+?)\"')
        list_price = list_price_reg.findall(sel.response.body)
        if len(list_price) != 0:
            data = list_price[0].strip()
            list_price_number = data[data.rfind(';') + 1:]
            list_price = self._format_price('USD', list_price_number)
            if list_price != item['price'] :
                item['list_price'] = list_price

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
        id_xpath = '//div[@class="detail-column"]/header/h4/text()'
        data = sel.xpath(id_xpath).extract()
        if len(data) == 0:
            return []
        id = data[0]
        review_url = 'http://saksfifthavenue.ugc.bazaarvoice.com/5000-en_us/idnum/reviews.djs?format=embeddedhtml'
        review_url = review_url.replace('idnum', id)
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('"numReviews":')
        if indx1 == -1:
            item['review_count'] = 0
            return []
        indx2 = content.find(',', indx1)
        data = content[indx1 + len('"numReviews":'):indx2]
        review_count = 0
        if len(data) != 0:
            review_count = int(data)
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        indx1 = content.find('"avgRating":')
        indx2 = content.find(',', indx1)
        data = content[indx1 + len('"avgRating":'):indx2]
        item['review_rating'] = float(data)
        review_num = 0;
        review_url0 = review_url
        pageidx = 0
        review_list = []
        while review_num < review_count:
            pageidx += 1
            pagenum = str(pageidx)
            review_url = review_url0 + '&page=' + pagenum + '&'
            request = urllib2.Request(review_url)
            response = urllib2.urlopen(request)
            content = []
            content = response.read()
            indx = content.find('BVSubmissionPopupContainer')
            tp = 0
            if indx == -1:
                indx = content.find('BVRRRatingsOnlySummaryTitle')
                tp = 1
                if indx == -1:
                    review_num += 1
            while indx != -1:
                rating = 0
                date = ''
                name = ''
                cont = ''
                title = ''
                if tp == 0:
                    indx += len('BVSubmissionPopupContainer')
                else:
                    indx += len('BVRRRatingsOnlySummaryTitle')
                indx1 = content.find('BVRRNumber BVRRRatingNumber', indx)
                if indx1 != -1:
                    indx1 += len('BVRRNumber BVRRRatingNumber')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    data = content[indx2:indx3]
                    rating = float(data)
                indx1 = content.find('BVRRValue BVRRReviewDate', indx)
                if indx1 != -1:
                    indx1 += len('BVRRValue BVRRReviewDate')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    date = content[indx2:indx3]
                indx1 = content.find('BVRRNickname', indx)
                if indx1 != -1:
                    indx1 += len('BVRRNickname')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    name = content[indx2:indx3 - 1]
                indx1 = content.find('BVRRValue BVRRReviewTitle', indx)
                if indx1 != -1:
                    indx1 += len('BVRRValue BVRRReviewTitle')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    title = content[indx2:indx3]
                indx1 = content.find('span class=\\"BVRRReviewText\\"', indx)
                if indx1 != -1:
                    indx1 += len('span class=\\"BVRRReviewText\\"')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('span', indx2)
                    cont = content[indx2:indx3 - 3]
                review_list.append({'rating':rating,
                  'date':date,
                  'name':name,
                  'title':title,
                  'content':cont})
                indx = content.find('BVSubmissionPopupContainer', indx)
                if indx == -1:
                    indx = content.find('BVRRRatingsOnlySummaryTitle', indx)
                review_num += 1
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
