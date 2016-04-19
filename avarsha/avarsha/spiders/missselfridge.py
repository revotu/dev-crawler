# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline
import urllib2
from avarsha_spider import AvarshaSpider


_spider_name = 'missselfridge'

class MissselfridgeSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["missselfridge.com"]
    is_last = False

    def __init__(self, *args, **kwargs):
        super(MissselfridgeSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if(idx1 != -1):
            parmt = url[idx1 + len('#'):]
            target1 = (
                'http://us.missselfridge.com/webapp/wcs/stores/servlet'
                '/CatalogNavigationSearchResultCmd?')
            url = (target1 + parmt
                .replace(' ', '%20').replace('^', '%5E')
                .replace('/', '%2F').replace('"', '%22')
                .replace('[', '%5B').replace(']', '%5D')
                .replace('{', '%7B').replace('}', '%7D'))
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//li[@class="product_description"]/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        if(self.is_last == True):
            return requests
        _show_last = 0
        _show_next = 0
        _show_last_xpath = '//li[@class="show_last"]/a/@href'
        data = sel.xpath(_show_last_xpath).extract()
        if(len(data) != 0):
            line = data[0]
            idx1 = line.find('beginIndex=')
            if(idx1 != -1):
                idx2 = line.find('&', idx1)
                if(idx2 != -1):
                    _show_last = int(line[idx1 + len('beginIndex='):idx2])
        nexts_xpath = '//li[@class="show_next"]/a/@href'
        nexts = sel.xpath(nexts_xpath).extract()
        if(len(nexts) != 0):
            line = nexts[0]
            idx1 = line.find('beginIndex=')
            if(idx1 != -1):
                idx2 = line.find('&', idx1)
                if(idx2 != -1):
                    _show_next = int(line[idx1 + len('beginIndex='):idx2])
            if(_show_next == _show_last):
                self.is_last = True
            idx1 = line.find('CatalogNavigationSearchResultCmd?')
            if(idx1 != -1):
                _temp = line[idx1 + len('CatalogNavigationSearchResultCmd?'):]
                _temp = (_temp.replace(' ', '%20').replace('^', '%5E')
                    .replace('/', '%2F').replace('"', '%22')
                    .replace('[', '%5B').replace(']', '%5D')
                    .replace('{', '%7B').replace('}', '%7D'))
                line = (
                    line[:idx1 + len('CatalogNavigationSearchResultCmd?')]
                    + _temp)
            list_url = line
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="tab frame"]/h1[1]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Missselfridge'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Missselfridge'

    def _extract_sku(self, sel, item):
        sku_xpath = '//li[@class="product_code"]/span/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = str(data[0])

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="product_description"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        _thumbnails = []
        _default_url = ''
        for line in sel.response.body.split('\n'):
            idx = line.find('thumbnails: [')
            if(idx != -1):
                while(True):
                    idx1 = line.find('"')
                    if(idx1 != -1):
                        idx2 = line.find('"', idx1 + len('"'))
                        _thumbnails.append(line[idx1 + len('"'):idx2])
                        line = line[idx2 + len('"'):]
                    else:
                        break
                break
        default_url_xpath = '//a[@title="Zoom in"]/@href'
        data = sel.xpath(default_url_xpath).extract()
        if(len(data) != 0):
            _default_url = data[0]
            imgs.append(_default_url)
        idx1 = _default_url.rfind('/')
        if(idx1 != -1):
            idx2 = _default_url.find('_', idx1)
            if(idx2 != -1):
                for element in _thumbnails:
                    if(len(element) > 1):
                        _image_url = (
                            _default_url[:idx2] + element + _default_url[idx2:])
                        imgs.append(_image_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = (
            '//ul[@class="product_summary"]'
            '/li[@class="now_price product_price"]/span/text()')
        price2_xpath = '//li[@class="product_price"]/span/text()'
        data = sel.xpath(price_xpath).extract()
        data2 = sel.xpath(price2_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]')
            new_data = data_re.sub('', data[0])
            item['price'] = self._format_price('USD', new_data)
        elif len(data2) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]')
            new_data = data_re.sub('', data2[0])
            item['price'] = self._format_price('USD', new_data)

    def _extract_list_price(self, sel, item):
        list_price_xpath = (
            '//ul[@class="product_summary"]'
            '/li[@class="was_price product_price"]/span/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]')
            new_data = data_re.sub('', data[0])
            item['list_price'] = self._format_price('USD', new_data)

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

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        product_id_xpath = '//li[@class="product_code"]/span/text()'
        data = sel.xpath(product_id_xpath).extract()
        id = ''
        if len(data) == 0:
            return []
        else:
            id = data[0]
        review_url = 'http://missselfridge.ugc.bazaarvoice.com/6029-en_gb/idnum/reviews.djs?format=embeddedhtml'
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
