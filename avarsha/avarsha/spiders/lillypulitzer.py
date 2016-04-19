# -*- coding: utf-8 -*-
# author: wanghaiyi

import re
import urllib2
import scrapy.cmdline

from avarsha_spider import AvarshaSpider
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

_spider_name = "lillypulitzer"

class LillypulitzerSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["lillypulitzer.com"]

    def __init__(self, *args, **kwargs):
        super(LillypulitzerSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.lillypulitzer.com'
        items_xpath = '//a[@class="thumbLink"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.lillypulitzer.com'
        nexts_xpath = '//div[@class="next"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def add_url(self, img_name):
        img_url = ('http://sugartown.scene7.com/is/image/sugartown/'
        + img_name + '?wid=675&hei=1125')
        return img_url

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@id="descriptionContainer"]//h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('\n+|\r+|\t+|  +')
            data[0] = data_re.sub('', data[0])
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Lillypulitzer'

    def _extract_brand_name(self, sel, item):
        pass

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@id="styleNumberDisplay"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][data[0].find(':'):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class='
        '"descriptionContainer six columns alpha"]//div')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
            data[0] = data_re.sub('', data[0])
            data[1] = data_re.sub('', data[1])
            data[2] = data_re.sub('', data[2])
            item['description'] = ''.join([data[0], data[1], data[2]])

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        mark_start = '3x","caption":"","src":"'
        for line in sel.response.body.split('"altSrc":"'):
            idx1 = line.find(mark_start)
            if idx1 != -1:
                idx2 = line.find('"},', idx1)
                img_name = line[idx1 + len(mark_start):idx2]
                img_url = self.add_url(img_name)
                imgs.append(img_url)
                if img_name[len(img_name) - 1] == '1':
                    img_name = img_name[0:len(img_name) - 3]
                    img_url = self.add_url(img_name)
                    imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@id="priceContainer"]'
            '//span[@class="origPrice"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0][len('$'):].strip())

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
        product_id_xpath = '//input[@name="productId"]/@value'
        data = sel.xpath(product_id_xpath).extract()
        id = ''
        if len(data) == 0:
            return []
        else:
            id = data[0]
        review_url = 'http://lillypulitzer.ugc.bazaarvoice.com/7574/idnum/reviews.djs?format=embeddedhtml'
        review_url = review_url.replace('idnum', id)
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('BVRRCount BVRRNonZeroCount')
        if indx1 == -1:
            item['review_count'] = 0
            return []
        indx1 = content.find('BVRRNumber', indx1)
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
        indx3 = content.find('/', indx2)
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
