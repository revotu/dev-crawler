# -*- coding: utf-8 -*-
# author: tanyafeng

import re
import urllib2
import cookielib

import scrapy.cmdline
from scrapy import log
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'bloomingdales'

class BloomingdalesSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["bloomingdales.com"]

    def __init__(self, *args, **kwargs):
        super(BloomingdalesSpider, self).__init__(*args, **kwargs)

        settings = get_project_settings()
        settings.set('cookies_enabled', 'true')

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        """use convert_url to split '#' in item_url"""

        base_url = ''
        items_xpath = '//*[@class="imageLink productThumbnailLink"]/@href'

        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = self.convert_url(path)
            if path.find(base_url) == -1:
                item_url = base_url + self.convert_url(path)
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        prev_cookies = sel.response.headers.getlist('Set-Cookie')
        curr_cookie = ''
        for tmp_cookie in prev_cookies:
            if tmp_cookie.find('akaau') != -1:
                curr_cookie = 'shippingCountry=US; ' + tmp_cookie
                break

        requests = []
        result_url = ''
        keywords = ''
        category_id = ''
        page_str_xpath = '//*[@class="pageNumber"]'
        page_str = sel.xpath(page_str_xpath).extract()
        if len(page_str) != 0:
            max_page_str = re.findall('>(.*?)<', page_str[len(page_str) - 1])
            category_str = re.findall('CategoryID=(\\w*)', page_str[0])
            max_page_num = int(max_page_str[0])
            if sel.response.url.find('search') == -1:
                category_id = category_str[0]

            for page_num in range(2 , max_page_num + 1):
                self.log('Parse category pagenum: %d' % page_num, log.DEBUG)
                if sel.response.url.find('search') == -1:
                    fetch_next_url = ('http://www1.bloomingdales.com/catalog/'
                        'category/facetedmeta?edge=hybrid&parentCategoryId='
                        'undefined&categoryId=%s&dynamicfacet=true&pageIndex'
                        '=%d&sortBy=ORIGINAL&productsPerPage=96&&'
                        'shipingCountry=US') % (category_id, page_num)
                else:
                    idx = sel.response.url.find('keyword=')
                    keywords = sel.response.url[idx + len('keyword='):]
                    fetch_next_url = ('http://www1.bloomingdales.com/shop/'
                        'search/facetedmeta?edge=hybrid&keyword=%s&pageIndex='
                        '%d&sortBy=ORIGINAL&productsPerPage=96&') % \
                        (keywords, page_num)

                opener = urllib2.build_opener(urllib2.\
                    HTTPCookieProcessor(cookielib.CookieJar()))
                urllib2.install_opener(opener)
                req = urllib2.Request(fetch_next_url)
                req.add_header('Cookie', curr_cookie)
                content = urllib2.urlopen(req).read()
                match = re.findall('id="metaProductIds".*?\\[(.*?)\\]', content)
                if sel.response.url.find('search') == -1:
                    result_url = ('http://www1.bloomingdales.com/shop/catalog/'
                        'product/thumbnail/1?edge=hybrid&limit'
                        '=none&ids=%s') % (match[0].replace(' ', ''))
                else:
                    result_url = ('http://www1.bloomingdales.com/shop/search/'
                        'product/thumbnail?edge=hybrid&limit=none&keyword'
                        '=%s&ids=%s') % (keywords , match[0].replace(' ', ''))
                list_urls.append(result_url)
                requests.append(scrapy.Request(result_url, \
                    callback=self.parse))

        return requests

    def convert_url(self, url):
        url_str = url.split('#')
        return url_str[0]

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="productTitle"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Bloomingdales'

    def _extract_brand_name(self, sel, item):
        brand_pattern = re.compile('brandName\W*"(.*?)"')
        for line in sel.response.body.split('\n'):
            if line.find('var brandName =') != -1:
                match = brand_pattern.findall(line)
                if len(match) != 0:
                    item['brand_name'] = match[0]
                break

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@id="productId"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@id="pdp_tabs_body_details"]/div/node()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        """primaryImages"""
        for line in sel.response.body.split('\n'):
            idx1 = line.find('primaryImages[')
            if idx1 != -1:
                img_pattern = re.compile(':"(.*?)"')
                match = img_pattern.findall(line)
                for img_str in match:
                    for sub_img_str in img_str.split(','):
                        img_url = ('http://images.bloomingdales.com/is/image'
                            '/BLM/products/%s?wid=1200&qlt=90,0&layer'
                            '=comp&op_sharpen=0&resMode=sharp2&op_usm'
                            '=0.7,1.0,0.5,0&fmt=jpeg') % sub_img_str
                        imgs.append(img_url)
                break
        """additionalImages"""
        for line in sel.response.body.split('\n'):
            idx2 = line.find('additionalImages[')
            if idx2 != -1:
                img_pattern = re.compile(':"(.*?)"')
                match = img_pattern.findall(line)
                for img_str in match:
                    for sub_img_str in img_str.split(','):
                        img_url = ('http://images.bloomingdales.com/is/image'
                            '/BLM/products/%s?wid=1200&qlt=90,0&layer'
                            '=comp&op_sharpen=0&resMode=sharp2&op_usm'
                            '=0.7,1.0,0.5,0&fmt=jpeg') % sub_img_str
                        imgs.append(img_url)
                break
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        multi_color_list = []
        color_pattern = re.compile('"color".*?"(.*?)".*?"In Stock:')
        for line in sel.response.body.split('\n'):
            if line.find('upcID') != -1:
                for subline in line.split('},{'):
                    color_match = color_pattern.findall(subline)
                    for result in color_match:
                        multi_color_list.append(result)
                break
        item['colors'] = list(set(multi_color_list))

    def _extract_sizes(self, sel, item):
        size_xpath = '//*[@class="size regular"]/@data-product-displaysize'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@class="netPrice"]/@value'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@class="priceBig"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0][len('$'):].strip()
            if item['price'].find(list_price_number) == -1:
                item['list_price'] = self._format_price('USD', \
                    list_price_number)

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
        indx1 = url.find("?ID=") + len("?ID=")
        indx2 = url.find("&", indx1)
        id = ''
        if indx2 != -1:
            id = url[indx1:indx2]
        else:
            id = url[indx1:]
        review_url = 'http://bloomingdales.ugc.bazaarvoice.com/7130aa/idnum/reviews.djs?format=embeddedhtml'
        review_url = review_url.replace('idnum', id)
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('BVRRCount BVRRNonZeroCount')
        if indx1 == -1:
            item['review_count'] = 0
            return []
        indx2 = content.find('BVRRNumber', indx1) + len('BVRRNumber')
        indx2 = content.find('>', indx2) + len('>')
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
                data = ''
                name = ''
                cont = ''
                title = ''
                if tp == 0:
                    indx += len('BVSubmissionPopupContainer')
                else:
                    indx += len('BVRRRatingsOnlySummaryTitle')
                indx1 = content.find('BVRRNumber BVRRRatingNumber', indx) + len('BVRRNumber BVRRRatingNumber')
                if indx1 != -1:
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    data = content[indx2:indx3]
                    rating = float(data)
                indx1 = content.find('BVRRValue BVRRReviewDate', indx) + len('BVRRValue BVRRReviewDate')
                if indx1 != -1:
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    date = content[indx2:indx3]
                if indx1 != -1:
                    indx1 = content.find('BVRRNickname', indx) + len('BVRRNickname')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    name = content[indx2:indx3]
                if indx1 != -1:
                    indx1 = content.find('BVRRValue BVRRReviewTitle', indx) + len('BVRRValue BVRRReviewTitle')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    title = content[indx2:indx3]
                if indx1 != -1:
                    indx1 = content.find('span class=\\"BVRRReviewText\\"', indx) + len('span class=\\"BVRRReviewText\\"')
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
