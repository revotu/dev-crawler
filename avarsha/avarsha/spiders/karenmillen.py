# -*- coding: utf-8 -*-
# author: zhujun

import scrapy.cmdline

import re

import urllib2

from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'karenmillen'

class KarenmillenSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["karenmillen.com"]

    def __init__(self, *args, **kwargs):
        self.header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'}
        super(KarenmillenSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        if url.find('search?') != -1:
            return url
        else:
            match = re.search(re.compile('filters=[^&]+'), url)
            if match == None:
                self.filters = ''
            else:
                self.filters = match.group()[len('filters='):]
            match = re.match(re.compile('http://www.karenmillen.com/[^/]+'), url)
            self.value = match.group()[len('http://www.karenmillen.com/'):]
            url = ('http://www.karenmillen.com/pws/AJProductFiltering.ice?'
                'layout=ajaxlist.layout&value=%s&paId=wc_dept&filters=%s'
                '&page=0&loadCat=true&view=3' % (self.value, self.filters))
            return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        if sel.response.url.find('search?') != -1:
            match = re.search(re.compile('&w=[^&]+'), sel.response.url)
            self.search = match.group()[len('&w='):]
            match = re.search(re.compile('af=[^&]*'), sel.response.url)
            if match != None:
                self.af = match.group()[len('af='):]
            else:
                self.af = ''
            data = sel.xpath('//*[@class="totalResults"]/text()').re('\d+')
            total = int(data[0])
            num = 0
            requests = []
            while True:
                curl = ('http://fashion.karenmillen.com/search?p=Q&lbc='
                    'karenmillen&uid=565522685&w=%s&isort=priority&method=and&'
                    'view=grid&af=%s&country=GB&ts=infinitescroll&srt=%d' \
                    % (self.search, self.af, num))
                request = urllib2.Request(url=curl, headers=self.header);
                sel = Selector(text=urllib2.urlopen(request).read())
                items_xpath = '//li[contains(@id, "product")]/a[1]//@href'
                data = sel.xpath(items_xpath).extract()
                for item_url in data:
                    item_urls.append(item_url)
                    requests.append(
                        scrapy.Request(item_url, callback=self.parse_item))
                if num + 20 >= total:
                    break
                num += 20
            return requests

        base_url = ''
        items_xpath = '//ul[@id="main_products_list_page"]//li/a/@href'
        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        if sel.response.url.find('search?') == -1:
            base_url = ''
            nexts_xpath = (
                '//ul[contains(@class="pagination", @id="top_pagination")]'
                '/li[@class="next"]/a/@href')
            # don't need to change this line
            return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)
        else:
            return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@id="product_title"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Karenmillen'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'KM'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[contains(@data-product-id, "")]/@data-product-id'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@id="editor_notes"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ' '.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        image_xpath = '//*[@id=\'enlarged_image\']/@src'
        data = sel.xpath(image_xpath).extract()
        imgs = []
        if len(data) != 0:
            imgs.append(data[0])
            idx1 = data[0].rfind('/')
            idx2 = data[0].rfind('.')
            img_num = data[0][idx1 + 1:idx2]
            for i in xrange(1, 10):
                img_url = ('http://media.karenmillen.com/pws/client/images'
                    '/catalogue/products/%s/zoom/%s_%d.jpg' \
                    % (img_num, img_num, i))
                try:
                    urllib2.urlopen(img_url)
                    imgs.append(img_url)
                except:
                    break
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//*[@id="colour_variants"]/ul/li/span/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) == 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//li[@class="in_stock "]/label/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            sizes = []
            for size in data:
                if len(size.strip()) != 0:
                    sizes.append(size.strip())
            item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@class="product_price"]/text()'
        price1_xpath = '//*[@class="product_price"]/span[@class="now"]/text()'
        data = sel.xpath(price_xpath).re('\d.*\d')
        if len(data) != 0:
            price_number = data[0]
            item['price'] = self._format_price('GBP', price_number)
        else:
            data = sel.xpath(price1_xpath).re('\d.*\d')
            if len(data) != 0:
                price_number = data[0]
                item['price'] = self._format_price('GBP', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@class="product_price"]/span[@class="was"]/text()'
        data = sel.xpath(list_price_xpath).re('\d.*\d')
        if len(data) != 0:
            list_price_number = data[0]
            item['list_price'] = self._format_price('GBP', list_price_number)

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
        content = sel.response.body
        indx1 = content.find('UNIQUE_PRODUCT_BV =')
        indx2 = content.find('"', indx1) + len('"')
        indx3 = content.find('"', indx2)
        id = ''
        if indx1 == -1:
            return []
        else:
            id = content[indx2:indx3]
        review_url = 'http://karenmillen.ugc.bazaarvoice.com/8023-en_gb/idnum/reviews.djs?format=embeddedhtml'
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
