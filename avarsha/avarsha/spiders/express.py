# -*- coding: utf-8 -*-
# author: yangxiao

import re
import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'express'

class ExpressSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ['express.com', 'images.express.com']

    def __init__(self, *args, **kwargs):
        super(ExpressSpider, self).__init__(*args, **kwargs)

    def _find_items_from_list_page(self, sel, base_url, items_xpath, item_urls):
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            if ' ' in item_url:
                item_url = item_url.replace(' ', '%20')
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.express.com'
        items_xpath = '//ul[@class="product-info"]/li/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.express.com'
        nexts_xpath = '//a[@class="right-arrow"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h2[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'express'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'express'

    def _extract_sku(self, sel, item):
        item['sku'] = re.search('sku: "(.*?)"', sel.response.body).group(1)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_title_xpath = ('//div[@class="product-description"]/*')
        description_content_xpath = ('//div[@class="fabric-care"]/*')
        data = []
        title = sel.xpath(description_title_xpath).extract()
        if len(title) != 0:
            data.append(title[0])
        content = sel.xpath(description_content_xpath).extract()
        if len(content) != 0:
            data += content
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_list_xpath = '//ul[@id="express-view-images-list"]/li/a/@href'
        data = sel.xpath(imgs_list_xpath).extract()
        if len(data) != 0:
            img_code_list = self.__collect_image_code(sel.response, data[0])
        image_urls = []
        for img_code in img_code_list:
            image_url = ('http://images.express.com/is/image/expressfashion/'
                '%s?cache=on&wid=640&fmt=jpeg&qlt=70,1&resmode=sharp2'
                '&op_usm=1,1,5,0&fit=fit,1'
                '&defaultImage=new_Photo-Coming-Soon' % img_code)
            image_urls.append(image_url)
        item['image_urls'] = image_urls

    def _extract_colors(self, sel, item):
        color_xpath = '//ul[@id="express-view-colors"]/li/label/@title'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//select[@name="express-view-sizes-dropdown"]/option\
            /text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data[1:]

    def _extract_stocks(self, sel, item):
        pass

    def _extract_prices(self, sel, item):
        self._extract_list_price(sel, item)
        self._extract_price(sel, item)
        self._extract_low_price(sel, item)
        self._extract_high_price(sel, item)

    def _extract_price(self, sel, item):
        if item.get('list_price') != None:
            price_xpath = '//div[@itemprop="offers"]/h4[@class="sale"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = re.search('\$(.*)$', data[1]).group(1)
                item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = '//span[@itemprop="price"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = re.search('\$(.*)$', data[0]).group(1)
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@itemprop="offers"]/h4[@class="sale"]/span'
            '/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = re.search('\$(.*)$', data[0]).group(1)
            item['list_price'] = self._format_price('USD', price_number)

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
        product_id_xpath = '//span[@class="brdcrmb-style-code"]/text()'
        data = sel.xpath(product_id_xpath).extract()
        id = ''
        if len(data) == 0:
            return []
        else:
            id = data[0]
        review_url = 'http://express.ugc.bazaarvoice.com/6549/idnum/reviews.djs?format=bulkembeddedhtml'
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

    def __collect_image_code(self, response, image_url):
        base_url = ('http://images.express.com/is/image/expressfashion'
            '?req=set,json&cache=on&imageSet=')
        default_image_code = re.search('/(new.*?)\?', image_url).group(1)
        image_code_url = base_url + default_image_code
        content = urllib2.urlopen(image_code_url).read()
        image_code_list = re.findall('"n":"expressfashion/(.*?)"', \
            content)
        return image_code_list

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
