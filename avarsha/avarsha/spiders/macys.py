# -*- coding: utf-8 -*-
# author: huoda

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings
from scrapy import log

from avarsha_spider import AvarshaSpider


_spider_name = 'macys'

class MacysSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["macys.com"]

    user_agent = ''

    def __init__(self, *args, **kwargs):
        super(MacysSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www1.macys.com'
        items_xpath = ('//li[@class="productThumbnail"]//div'
            '[@class="shortDescription"]/a//@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        id_xpath = '//div[@class="current cat"]//@id[1]'
        data = sel.xpath(id_xpath).extract()
        if len(data) != 0:
            idd = data[0]
            pageIndex = 2
            data_xpath = '//div[@id="metaProductIds"]/text()'
            url1 = ('http://www1.macys.com/catalog/category/facetedmeta'
                '?edge=hybrid&categoryId=')
            url2 = '&facet=false&dynamicfacet=true&pageIndex='
            url3 = '&sortBy=ORIGINAL&productsPerPage=40&'
            url_1 = ('http://www1.macys.com/shop/catalog/product/thumbnail/1?'
                'edge=hybrid&limit=none&suppressColorSwatches=false&categoryId=')
            url_2 = '&ids='
            pre_url = url_1 + idd + url_2
            prelist_url = url1 + idd + url2 + str(pageIndex) + url3
            req = urllib2.Request(prelist_url)
            req.add_header('User-Agent', self.user_agent)
            page = urllib2.urlopen(req).read()
            sel_temp = Selector(text=page)
            data = sel_temp.xpath(data_xpath).extract()
            while len(data) != 0:
                data = data[0]
                data = data[1:-1]
                ids = data.split(',')
                list_url = pre_url
                for iddd in ids:
                    iddd = iddd.strip()
                    iddd = idd + '_' + iddd
                    list_url = list_url + iddd + ','
                list_url = list_url[:-1]
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
                pageIndex += 1
                prelist_url = url1 + idd + url2 + str(pageIndex) + url3
                req = urllib2.Request(prelist_url)
                req.add_header('User-Agent', self.user_agent)
                page = urllib2.urlopen(req).read()
                sel_temp = Selector(text=page)
                data = sel_temp.xpath(data_xpath).extract()
        else:
            if 'search' in self.start_urls[0]:
                flag = self.start_urls[0].find('search?')
                tab = self.start_urls[0][flag + 7:]
                idd = '0'
                pageIndex = 2
                data_xpath = '//div[@id="metaProductIds"]/text()'
                url1 = ('http://www1.macys.com/shop/search/'
                    'facetedmeta?edge=hybrid&')
                url2 = '&facet=false&dynamicfacet=true&pageIndex='
                url3 = '&sortBy=ORIGINAL&productsPerPage=40&'
                url_1 = ('http://www1.macys.com/shop/search/product/'
                    'thumbnail?edge=hybrid&')
                url_2 = '&ids='
                pre_url = url_1 + tab + url_2
                prelist_url = url1 + tab + url2 + str(pageIndex) + url3
                req = urllib2.Request(prelist_url)
                req.add_header('User-Agent', self.user_agent)
                page = urllib2.urlopen(req).read()
                sel_temp = Selector(text=page)
                data = sel_temp.xpath(data_xpath).extract()
                while (len(data) != 0) & (len(data[0]) > 7):
                    data = data[0]
                    data = data[1:-1]
                    ids = data.split(',')
                    list_url = pre_url
                    for iddd in ids:
                        iddd = iddd.strip()
                        iddd = idd + '_' + iddd
                        list_url = list_url + iddd + ','
                    list_url = list_url[:-1]
                    list_urls.append(list_url)
                    request = scrapy.Request(list_url, callback=self.parse)
                    requests.append(request)
                    pageIndex += 1
                    prelist_url = url1 + tab + url2 + str(pageIndex) + url3
                    req = urllib2.Request(prelist_url)
                    req.add_header('User-Agent', self.user_agent)
                    page = urllib2.urlopen(req).read()
                    sel_temp = Selector(text=page)
                    data = sel_temp.xpath(data_xpath).extract()

        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="productTitle"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()
        available_xpath = '//ul[@class="similarItems"]/li/span/text()'
        data = sel.xpath(available_xpath).extract()
        if len(data) != 0:
            if 'currently unavailable' in data[0]:
                self.log('item ' + item['title'] + ' is currently unavailable')

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'macys'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@id="brandLogo"]/img//@alt'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()
        # not easy to scrap all the brands. at present this part of code
        # can only get brands which it has its only brandlogo picture.

    def _extract_sku(self, sel, item):
        sku_xpath = '//meta[@itemprop="productID"]//@content'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]
        else:
            sku_xpath = '//*[@id="productId"]//@value'
            data = sel.xpath(sku_xpath).extract()
            if len(data) != 0:
                item['sku'] = data[0]

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="productDetailsBody"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@id="imageZoomer"]/noscript//img//@src'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            img_urls = []
            for img in data:
                flag = img.find('wid=')
                img = img[:flag + 4] + '1400'
                img_urls.append(img)
            if len(img_urls) != 0:
                item['image_urls'] = img_urls
        else:
            img_xpath = '//div[@class="productImageSection"]/img//@src'
            data = sel.xpath(img_xpath).extract()
            if len(data) != 0:
                img_urls = []
                for img in data:
                    img_urls.append(img)
                if len(img_urls) != 0:
                    item['image_urls'] = img_urls

    def _extract_colors(self, sel, item):
        color_xpath = '//div[@class="colors"]//img[@class="colorSwatch"]//@title'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//div[@class="sizes"]//li[@class="horizontal size"]//text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            sizes = []
            for size in data:
                size = size.strip()
                if len(size) != 0:
                    sizes.append(size)
            if len(sizes) != 0:
                item['sizes'] = sizes

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="standardProdPricingGroup"]'
            '/span[@class="priceSale"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0]
            flag = price_number.find('$')
            item['price'] = self._format_price('USD', price_number[flag + 1:])
            list_price_xpath = ('//div[@class="standardProdPricingGroup"]'
                '/span[1]/text()')
            data = sel.xpath(list_price_xpath).extract()
            if (len(data) != 0) & ('Orig' in data[0]):
                list_price_number = data[0]
                flag = list_price_number.find('$')
                item['list_price'] = self._format_price('USD', \
                    list_price_number[flag + 1:])
        else:
            price_xpath = '//div[@class="standardProdPricingGroup"]/span/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0]
                flag = price_number.find('$')
                item['price'] = self._format_price('USD', \
                    price_number[flag + 1:])
            else:
                item['price'] = self._format_price('USD', '0')

    def _extract_list_price(self, sel, item):
        pass
    def _extract_review_list(self, sel, item):
        product_id_xpath = '//meta[@itemprop="productID"]/@content'
        data = sel.xpath(product_id_xpath).extract()
        id = ''
        if len(data) == 0:
            return []
        else:
            id = data[0]
        review_url = 'http://macys.ugc.bazaarvoice.com/7129-nowrite/idnum/reviews.djs?format=embeddedhtml'
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
