# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

import urllib2

from avarsha_spider import AvarshaSpider


_spider_name = 'nike'

class NikeSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["nike.com"]

    def __init__(self, *args, **kwargs):
        super(NikeSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        idx1 = sel.response.url.find('pw/')
        if idx1 == -1:
            return []
        idx2 = sel.response.url.find('?')
        if idx2 == -1:
            category = sel.response.url[idx1 + len('pw/'):]
            tail_url = ''
        else:
            category = sel.response.url[idx1 + len('pw/'):idx2]
            tail_url = '&' + sel.response.url[idx2 + 1:]

        page, requests = 1, []
        while True:
            base_url = ('http://store.nike.com/html-services/gridwallData?'
                'country=US&lang_locale=en_US&gridwallPath='
                '%s&pn=%d' % (category, page))
            request = urllib2.Request(base_url + tail_url)
            lines = urllib2.urlopen(request).read().split(',')
            for line in lines:
                idx1 = line.find('pdpUrl\":\"')
                if idx1 != -1:
                    idx2 = line.find('\"', idx1 + len('pdpUrl\":\"'))
                    if idx2 != -1:
                        item_url = line[idx1 + len('pdpUrl\":\"'):idx2]
                        if item_url.find('#') != -1:
                            continue
                        item_urls.append(item_url)
                        requests.append(scrapy.Request(item_url, \
                            callback=self.parse_item))

            if lines[0].find('nextPageDataService') != -1:
                page += 1
            else:
                break
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = (
            '//h1[@class="exp-product-title nsg-font-family--platform"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Nike'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Nike'

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@class="exp-style-color"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][len('Style: '):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//ul[@class="noindent"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line.strip()
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_url_xpath = '//img[@class="exp-pdp-alt-image"]/@data-large-image'
        data = sel.xpath(imgs_url_xpath).extract()
        imgs = []
        if len(data) != 0:
            for line in data:
                img_url = line + '?wid=1860&hei=1860&fmt=jpeg&qlt=85&bgc=F5F5F5'
                imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//select[@name="skuAndSize"]//option/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            idx = 0
            while idx < len(data):
                data[idx] = data[idx].strip()
                idx += 1
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@class="exp-pdp-local-price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD ', price_number)

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

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        id_xpath = '//input[@name="stylenumber"]/@value'
        data = sel.xpath(id_xpath).extract()
        if len(data) == 0:
            return []
        id = data[0]
        review_url = 'http://nike.ugc.bazaarvoice.com/9191-en_us/idnum/reviews.djs?format=embeddedhtml'
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
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
