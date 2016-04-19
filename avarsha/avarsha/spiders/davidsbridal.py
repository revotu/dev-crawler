# -*- coding: utf-8 -*-
# @author: wanghaiyi

import urllib
import urllib2
import json

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'davidsbridal'

class DavidsbridalSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["davidsbridal.com"]
    index = 1

    def __init__(self, *args, **kwargs):
        super(DavidsbridalSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@class="product_name"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//a[@class="paging-next"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//head/title/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Davidsbridal'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'David\'s Bridal'

    def _extract_sku(self, sel, item):
        shop_owner_sn_xpath = '//li[@class="active"]/text()'
        data = sel.xpath(shop_owner_sn_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_tmp = ''
        description_xpath = '//div[@class="truncated-text"]/p'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                description_tmp += data[i]
        description_detail_xpath = '//div[@class="full-text"]/ul'
        data = sel.xpath(description_detail_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                description_tmp += data[i]
        item['description'] = description_tmp

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        suffix = 1
        img_url_list = []
        color_list_xpath = ('//li[@class="quickShipClass"]/@id | //li'
            '[@class="allColorsClass"]/@id')
        data = sel.xpath(color_list_xpath).extract()
        img_tmp = 'http://img.davidsbridal.com/is/image/DavidsBridalInc/'
        idx1 = sel.response.body.strip('\n')
        idx1 = idx1.replace(' ', '')
        idx1 = idx1[idx1.find('productMainImage'):]
        if idx1.find('Set-') != -1:
            idx1 = idx1[idx1.find('Set-'):]
            idx2 = idx1[:idx1.find('?')]
            img_tmp1 = (img_tmp + idx2 + '?req=set,json,UTF-8&labelkey=label'
                + '&handler=s7sdkJSONResponse')
#         for i in range(len(data)):
#             idx_tmp = idx2[idx2.rfind('-') + 1:]
#             if data[i].find(' ') != -1:
#                 if data[i].replace(' ', '') == idx_tmp:
#                     idx2 = idx2[:idx2.rfind('-') + 1]
#                     idx3 = idx2 + data[i]
#                     idx3 = urllib.quote(idx3.encode('utf-8'))
#                     img_tmp1 = (img_tmp + idx3 + '?req=set,json,UTF-8&labelkey=label'
#                         + '&handler=s7sdkJSONResponse')
        try:
            img_tmp1
            content = urllib2.urlopen(img_tmp1).read()
        except Exception as err1:
            print 'Js is error'
        else:
            img_url_list = []
            content = content[content.find('{'):content.rfind(',')]
            content = json.loads(content)
            for i in range(len(content['set']['item'])):
                img = content['set']['item'][i]['i']['n']
                img_url = ('http://img.davidsbridal.com/is/image/' + img +
                    '?img=%d_%d&wid=1200&hei=1800&fmt=jpg' %(self.index , suffix))
                if img_url not in img_url_list:
                    img_url_list.append(img_url)
                    suffix += 1
        self.index += 1
        item['image_urls'] = img_url_list


    def _extract_colors(self, sel, item):
        color_list_xpath = ('//li[@class="quickShipClass"]/@id | //li'
            '[@class="allColorsClass"]/@id')
        data = sel.xpath(color_list_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        idx1 = sel.response.body
        idx1 = idx1.replace('\n' , '')
        while idx1.find('product_sale_price') != -1:
            idx_num_tmp = idx1.find('product_sale_price')
            idx1 = idx1[idx_num_tmp + 25:]
            price_tmp = idx1[:idx1.find('\"]')]
        item['price'] = self._format_price('USD', price_tmp)

    def _extract_list_price(self, sel, item):
        idx1 = sel.response.body
        idx1 = idx1.replace('\n' , '')
        while idx1.find('product_base_price') != -1:
            idx_num_tmp = idx1.find('product_base_price')
            idx1 = idx1[idx_num_tmp + 25:]
            price_tmp = idx1[:idx1.find('\"]')]
        if price_tmp != item['price'].replace('USD ' , ''):
            print price_tmp
            item['list_price'] = self._format_price('USD', price_tmp)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        idx1 = sel.response.body
        idx1 = idx1.replace('\n' , '')
        while idx1.find('product_sale_price') != -1:
            idx_num_tmp = idx1.find('product_sale_price')
            idx1 = idx1[idx_num_tmp + 25:]
            price_tmp = float(idx1[:idx1.find('\"]')])
        if price_tmp >= 99.0:
            item['is_free_shipping'] = True

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        alltext = sel.response.body
        indx1 = alltext.find("productId:") + len("productId:")
        indx2 = alltext.find('"', indx1) + len('"')
        indx3 = alltext.find('"', indx2)
        id = ''
        id = alltext[indx2:indx3]
        review_url = 'http://davidsbridal.ugc.bazaarvoice.com/7294-en_us/idnum/reviews.djs?format=embeddedhtml'
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
        indx1 = content.find('Overall Rating')
        indx1 = content.find('BVImgOrSprite', indx1)
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
            tp = 0
            if indx == -1:
                indx = content.find('BVRRRatingsOnlySummaryTitle')
                tp = 1
                if indx == -1:
                    review_num += 1
            while indx != -1:
                rating = 0
                data = ''
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
