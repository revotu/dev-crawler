# -*- coding: utf-8 -*-
# author: tanyafeng

import re
import urllib2

from scrapy.selector import Selector
import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'madewell'

class MadewellSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["madewell.com"]

    def __init__(self, *args, **kwargs):
        super(MadewellSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = ''
        items_xpath = '//*[@class="arrayCopy"]//@href'
        search_items_xpath = '//*[@class="product-section"]/figure/a/@href'

        item_nodes = sel.xpath(items_xpath).extract()
        if len(item_nodes) == 0:
            item_nodes = sel.xpath(search_items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(self.convert_url(item_url))
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        return []

    def convert_url(self, url):
        return url.replace(' ' , '%20')

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@property="og:title"]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Madewell'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Madewell'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@id="pdpMainImage0"]/img/@data-productcode'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="product_desc"]/node()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        pass

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        currency_str = []
        price_pattern = re.compile('ProductValue\',\'(.*?)\'')
        currency_pattern = re.compile('current_currency=\'(.*?)\'')
        for line in sel.response.body.split('\n'):
            match = currency_pattern.findall(line)
            if len(match) != 0:
                currency_str.append(match[0])
                break
        for line in sel.response.body.split('\n'):
            match = price_pattern.findall(line)
            if len(match) != 0:
                item['price'] = self._format_price(currency_str[0], match[0])
                break

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
        url = sel.response.url
        indx1 = url.find('.jsp')
        indx2 = url.rfind('/', 0, indx1) + len('/')
        id = ''
        if indx1 == -1:
            return []
        else:
            id = url[indx2:indx1]
        review_url = 'https://madewell.ugc.bazaarvoice.com/4778-en_us/idnum/reviews.djs?format=embeddedhtml'
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

    def _extract_basic_options(self, sel, item):
        size_pattern = re.compile('"outofstock":false.*?"size":"(.*?)"}')
        color_pattern = re.compile(('"outofstock":false,"'
                                   'colordisplayname":"(.*?)"'))

        fetch_color_url = ('https://www.madewell.com/browse2/ajax/product_deta'
                           'ils_ajax.jsp?sRequestedURL=https%%3A%%2F%%2F'
                           'www.madewell.com%%2Fmadewell_category%%2FDRESSES'
                           '%%2Fgoingoutpartydresses%%2FPRDOVR~%s%%2F%s.jsp&'
                           'prodCode=%s') % (item['sku'], \
                                             item['sku'], \
                                             item['sku'])
        content = urllib2.urlopen(fetch_color_url).read()
        idx1 = content.find('productDetailsJSON = \'')
        idx2 = content.find('var imgSelectedColor')
        if idx1 != -1 and idx2 != -1:
            size_color_str = content[idx1 : idx2]
            color_match = color_pattern.findall(size_color_str)
            color_list = list(set(color_match))
            if len(color_list) != 0:
                item['colors'] = color_list
            size_match = size_pattern.findall(size_color_str)
            if len(size_match) != 0:
                item['sizes'] = size_match


        imgs = []
        img_xpath = '//*[@id="pdpMainImg0"]/@src'
        img_str = sel.xpath(img_xpath).extract()
        img_str_pattern = re.compile('pdp_.*?\\$')
        img_url = img_str_pattern.sub('pdp_enlarge$', img_str[0])
        for tmp_char in ['_b?$', '_m?$', '_s?$']:
            tmp_pattern = re.compile('_.\\?\\$')
            imgs.append(tmp_pattern.sub(tmp_char, img_url))

        img_pattern = re.compile('url : \'(.*?_enlarge.)')
        for line in content.split('\n'):
            match = img_pattern.findall(line)
            for tmp_img in match:
                imgs.append(tmp_img)
        item['image_urls'] = imgs

        list_price_xpath = '//*[@class="full-price"]/span[1]/text()'
        data = Selector(text=content).xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):]
            item['list_price'] = self._format_price('USD', price_number)

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
