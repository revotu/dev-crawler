# -*- coding: utf-8 -*-
# @author: zhangliangliang

import urllib2

import scrapy.cmdline

from scrapy.selector import Selector

import re

from scrapy.http import HtmlResponse

from avarsha_spider import AvarshaSpider


_spider_name = 'whitehouseblackmarket'

class WhitehouseblackmarketSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["whitehouseblackmarket.com"]

    def __init__(self, *args, **kwargs):
        super(WhitehouseblackmarketSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        pattern = 'cat\w+'
        category_str = re.findall(re.compile(pattern), sel.response.url)
        pattern1 = 'Ntt=[^&]+'
        search_str = re.search(re.compile(pattern1), sel.response.url)
        if len(category_str) == 2:
            if category_str[1] == 'catsales':
                all_urls_url = ('http://www.whitehouseblackmarket.com/store/'
                    'product-list/?N=0&Nr=AND(OR(product.catalogId%3Acatalog180001)'
                    '%2CCategory_SalePromoClearance%3AsalePromoClearance)'
                    '&isSale=1&Ns=catsales_ranking||salepopularityIndex|1'
                    '&No=0&Nrpp=10000&_=1432359177225')
            else:
                all_urls_url = ('http://www.whitehouseblackmarket.com/store/'
                    'product-list/?Nr=AND(flatCat:%s(AND(catRuleNo:catNo))'
                    '&shCatId=%s&Ns=%s_ranking||product.popularityIndex|'
                    '1&No=0&Nrpp=10000&_=1431136865550' \
                    % (category_str[1], category_str[1], category_str[1]))
        else:
            if search_str != None:
                all_urls_url = ('http://www.whitehouseblackmarket.com/store/'
                    'product-list/?Dy=1&Nty=1&'
                    '%s&No=0&Nrpp=1000000' % search_str.group())

        items_xpath = ('//div[@id="shelfProducts"]/'
            'div[contains(@class, "product-capsule")]/a[1]/@href')
        request = urllib2.Request(all_urls_url)
        response = urllib2.urlopen(request)
        sel = Selector(text=response.read())

        all_item_urls = sel.xpath(items_xpath).extract()
        requests = []
        pre_url = 'http://www.whitehouseblackmarket.com'
        for last_url in all_item_urls:
            item_url = pre_url + last_url
            item_urls.append(item_url)
            requests.append(scrapy.Request(item_url, callback=self.parse_item))
        # don't need to change this line
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@id="product-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Whitehouseblackmarket'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'whbm'

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@class="style-id-number"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="product-description-inner"]/*'
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
        img_xpath = '//ul[@class="alt-images"]//li/img/@src'
        img_urls = sel.xpath(img_xpath).extract()
        idx = 0
        while idx < len(img_urls):
            img_urls[idx] = 'http://www.whitehouseblackmarket.com' + \
                img_urls[idx].replace('thumb', 'large')
            idx += 1
        item['image_urls'] = img_urls

    def _extract_colors(self, sel, item):
        color_xpath = (
            '//div[@class="swatches-wrapper columns"]/ul/li/@data-color-name')
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data[:1]

    def _extract_sizes(self, sel, item):
        sizes_xpath = (
            '//select[@class="product-size"]//option/@data-size-search-name')
        data = sel.xpath(sizes_xpath).extract()
        if len(data) != 0:
            le = len(data) / 5
            data = data[:le]
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = (
            '//div[@class="sku-price"]/span[3]/span[1]/@data-price-low')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0])

    def _extract_list_price(self, sel, item):
        list_price_xpath = (
            '//ul[@class="product-skus"]/li[1]/input/@data-orignal-price')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            item['list_price'] = self._format_price('USD', data[0][1:])

    def _extract_low_price(self, sel, item):
        price_xpath = (
            '//div[@class="sku-price"]/span[3]/span[1]/@data-price-low')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0])

    def _extract_high_price(self, sel, item):
        price_xpath = (
            '//div[@class="sku-price"]/span[3]/span[1]/@data-price-high')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0])

    def _extract_is_free_shipping(self, sel, item):
        pass

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_best_review_rating(self, sel, item):
        pass

    def _find_str(self, line, be, ed):
        idx1 = line.find(be)
        if idx1 == -1:
            return ''
        idx2 = line.find(ed, idx1 + len(be))
        if idx2 == -1:
            return ''
        return line[idx1 + len(be):idx2]

    def _extract_review_list(self, sel, item):
        item_url = sel.response.url
        idx1 = item_url.find('?')
        if idx1 == -1:
            return []
        idx2 = idx1 - 9
        if idx2 <= 0:
            return []
        num = item_url[idx2:idx1]
        pre_review_url = (
            'https://whitehouseblackmarket.ugc.bazaarvoice.com/3015-en_us/')
        last_review_url = '/reviews.djs?format=embeddedhtml'
        review_url = pre_review_url + num + last_review_url
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        body = response.read().replace('\\', '')
        response = HtmlResponse(url=review_url, body=body)
        reviews_xpath = '//div[contains(@id, "BVRRDisplayContentReviewID")]'
        reviews = response.selector.xpath(reviews_xpath).extract()
        if len(reviews) == 0:
            return []
        item['review_count'] = len(reviews)
        rating_sum = 0
        review_list = []
        for line in reviews:
            content_be = '<span class="BVRRReviewText">'
            content_ed = '</span>'
            content = self._find_str(line, content_be, content_ed)
            date_be = '<span class="BVRRValue BVRRReviewDate">'
            date_ed = '</span>'
            date = self._find_str(line, date_be, date_ed)
            name_be = '<span class="BVRRNickname">'
            name_ed = '</span>'
            name = self._find_str(line, name_be, name_ed)
            rating_be = '<div class="BVRRRatingNormalImage">'
            rating_ed = '</div>'
            rating_img = self._find_str(line, rating_be, rating_ed)
            rating = self._find_str(rating_img, 'title="', ' ')
            rating_sum += int(rating)
            title_be = '<span class="BVRRValue BVRRReviewTitle">'
            title_ed = '</span>'
            title = self._find_str(line, title_be, title_ed)
            review_list.append({'rating':int(rating),
                            'date':date, 'name':name,
                            'title':title, 'content':content})

        item['max_review_rating'] = 5
        item['review_rating'] = float(rating_sum / len(reviews) + 0.0)
        if len(review_list) != 0:
            item['review_list'] = review_list



def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
