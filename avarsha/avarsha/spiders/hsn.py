# -*- coding: utf-8 -*-
# @author: donglongtu

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'hsn'

class HsnSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["hsn.com"]

    def __init__(self, *args, **kwargs):
        super(HsnSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.hsn.com'
        items_xpath = ('//*[@class="item product-item module violated"]'
            '/@data-product-url')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.hsn.com'
        nexts_xpath = '//*[@class="next"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="product-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Hsn'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@class="brand-info"]/h2/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        idx_1 = sel.response.url.rfind('/')
        idx_2 = sel.response.url.find('?')
        if idx_2 != -1:
            prod_id = sel.response.url[idx_1 + 1:idx_2]
        else:
            prod_id = sel.response.url[idx_1 + 1:]
        if len(prod_id) != 0:
            item['sku'] = prod_id

    def _extract_features(self, sel, item):
        feat_url = ('http://www.hsn.com/products/producttab/get-product-tab?'
            'id=%s&tab=Details' % item['sku'])
        req = urllib2.Request(feat_url)
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        response = urllib2.urlopen(req).read()
        sel_feat = Selector(text=response)
        feature_dict = {}
        feature_keys_xpath = '//*[@class="key"]/text()'
        feature_values_xpath = '//*[@class="values"]/span/text()'
        feature_keys = sel_feat.xpath(feature_keys_xpath).extract()
        feature_values = sel_feat.xpath(feature_values_xpath).extract()

        if len(feature_keys) != 0 and len(feature_values) != 0:
            for i in range(len(feature_keys)):
                feature_dict[feature_keys[i]] = feature_values[i]
        item['features'] = feature_dict

    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_url_xpath = ('//*[@class="image-container"]/a/@data-zoom | '
            '//*[@class="product-image-thumbnails"]/a/@data-zoom')
        data = sel.xpath(img_url_xpath).extract()
        img_list = []
        if len(data) != 0:
            for img in data:
                index = img.find(',')
                img = 'http:' + img[index + 2:-len('"]')]
                img_list.append(img)
        item['image_urls'] = img_list

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//*[@class="product-price"]/text() | '
            '//*[@class="product-price sale"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            idx = price_number.find('-')
            if idx != -1:
                price_number = price_number[:idx].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@class="product-old-price"]/del/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0 :
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
        count_xpath = '//div[@itemprop="aggregateRating"]//span[@itemprop="reviewCount"]/text()'
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
        max_review_rating = 5
        item['max_review_rating'] = max_review_rating
        rating_xpath = '//div[@itemprop="aggregateRating"]//span[@itemprop="ratingValue"]/text()'
        data = sel.xpath(rating_xpath).extract()
        review_rating = 5.0
        if len(data) != 0:
            review_rating = float(data[0])
        item['review_rating'] = review_rating
        base_review_url = 'http://www.hsn.com/products/productreviews/get-product-reviews?encodedProductName='
        sort_url = '&recordsPerPage=10&sortTerm=rating&sortSequence=descending&'
        tail_url = '&ratingFilter=&lessman=false'
        url = sel.response.url
        ind1 = url.rfind('/')
        ind2 = url.rfind('/', 0, ind1 - 1)
        productname = ''
        if ind1 != -1 and ind2 != -1:
            productname = url[ind2 + len('/'):ind1]
        else:
            return []
        id_xpath = '//input[@id="webp_id"]/@value'
        id = sel.xpath(id_xpath).extract()
        if len(id) == 0:
            return []
        else:
            id = id[0];
        sku_xpath = '//input[@id="pfid"]/@value'
        sku = sel.xpath(id_xpath).extract()
        if len(sku) == 0:
            return []
        else:
            sku = sku[0];
        review_url = base_review_url + productname + '&id=' + id + '&page=' + str(1) + sort_url + 'sku=' + sku + tail_url
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        review_list = []
        pagenum = 0
        while 'class="clearfix"' in content:
            sel = Selector(text=content)
            review_rating_xpath = '//li[@class="clearfix"]/div[@class="info"]//div[@class="rateit-range"]/div/@style'
            review_date_xpath = '//li[@class="clearfix"]/div[@class="timestamp"]/time/text()'
            review_name_xpath = '//li[@class="clearfix"]/div[@class="info"]/div[@class="customer"]/span/text()'
            review_title_xpath = '//li[@class="clearfix"]/div[@class="info"]/div[@class="title"]/text()'
            review_content_xpath = '//li[@class="clearfix"]/div[@class="copy"]/p/text()'
            review_rating = sel.xpath(review_rating_xpath).extract()
            review_date = sel.xpath(review_date_xpath).extract()
            review_name = sel.xpath(review_name_xpath).extract()
            review_title = sel.xpath(review_title_xpath).extract()
            review_content = sel.xpath(review_content_xpath).extract()
            review_num = min(len(review_rating), len(review_date), len(review_name), len(review_title), len(review_content))
            if review_num != 0:
                for i in range(review_num):
                    indx1 = review_rating[i].find('width:') + len('width:')
                    indx2 = review_rating[i].find('%')
                    rate = float(review_rating[i][indx1:indx2]) / 100.0 * max_review_rating
                    ratings = rate
                    dates = review_date[i]
                    names = review_name[i]
                    titles = review_title[i]
                    conts = review_content[i]
                    review_list.append({'rating':ratings,
                                      'date':dates,
                                      'name':names,
                                      'title':titles,
                                      'content':conts})
            pagenum += 1
            review_url = base_review_url + productname + '&id=' + id + '&page=' + str(pagenum) + sort_url + 'sku=' + sku + tail_url
            request = urllib2.Request(review_url)
            response = urllib2.urlopen(request)
            content = ''
            content = response.read()
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
