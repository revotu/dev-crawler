# -*- coding: utf-8 -*-
# @author: donglongtu

import re
import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'loft'

class LoftSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["loft.com"]

    def __init__(self, *args, **kwargs):
        super(LoftSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.loft.com'
        items_xpath = '//*[@class="product row-1 column-1"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            if list_url.find('?') == -1:
                list_url = list_url.replace('&', '?&')
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//*[@rel="next"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Loft'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Loft'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@name="productId"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@id="details-panel"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_set_url = ('http://richmedia.channeladvisor.com/ViewerDelivery/pro'
            'ductXmlService?callback=productXmlCallbackImageColorChangeprofile'
            'id12017974itemid%s&profileid=12017974'
            '&itemid=%s&viewerid=350' % (item['sku'], item['sku']))
        response = urllib2.urlopen(img_set_url).read()
        imgs_reg = re.compile(r'"@path": "(.+?390)",')
        imgs = []
        data = imgs_reg.findall(response)
        for img in data:
            imgs.append(img.replace('recipeId=390', 'recipeName=pdlg1286x1480'))
        item['image_urls'] = imgs
    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//del/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()[len('$'):]
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
        product_id_xpath = '//aside/text()'
        data = sel.xpath(product_id_xpath).extract()
        id = ''
        if len(data) == 0:
            return []
        else:
            data[0] = data[0].replace('#', '')
            id = data[0]
        review_url = 'http://anntaylorloft.ugc.bazaarvoice.com/0063redes-en_us/idnum/reviews.djs?format=embeddedhtml'
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
