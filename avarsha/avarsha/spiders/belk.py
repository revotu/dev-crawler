# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline
import urllib2
from avarsha_spider import AvarshaSpider


_spider_name = 'belk'

class BelkSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["belk.com"]

    def __init__(self, *args, **kwargs):
        super(BelkSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.belk.com'
        items_xpath = '//div[@class="image qv_image"]/a/@href'
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            idx = item_url.find('?')
            if(idx != -1):
                item_url = item_url[:idx]
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.belk.com'
        nexts_xpath = ('//ul[@class="pagination"]//li[@class="next"]/a/@rel'
            '|//ul[@class="pagination"]//li[@class="next"]/a/@href')
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if(path.find('javascript:;') != -1):
                continue
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_urls.append(list_url)
            requests.append(scrapy.Request(list_url, callback=self.parse))
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@id="prod_options"]//span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Belk'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Belk'

    def _extract_sku(self, sel, item):
        sku = ''
        for line in sel.response.body.split('\n'):
            idx1 = line.find('productId:')
            if(idx1 != -1):
                idx2 = line.rfind("'")
                sku = line[idx1 + len('productId:'):idx2].strip()
        item['sku'] = str(sku)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_overall_xpath = '//div[@id="description_panel"]'
        data = sel.xpath(description_overall_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        image_url = ''
        imgs_url_xpath = '//div[@class="alternate_images"]//a/img/@src'
        imgs_url2_xpath = '//div[@class="image_wrap"]//a/img/@src'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        data2_imgs = sel.xpath(imgs_url2_xpath).extract()
        if len(data_imgs) != 0:
            for image_url in data_imgs:
                imgs.append(self._get_image(image_url))
        elif len(data2_imgs) != 0:
            imgs.append(self._get_image(data2_imgs[0]))
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        list_price_xpath = '//span[@class="original_price"]/text()'
        list_price_data = sel.xpath(list_price_xpath).extract()
        price_xpath = '//span[@class="sale_price"]/text()'
        data_sale_price = sel.xpath(price_xpath).extract()
        price_xpath = '//span[@class="price"]/text()'
        data_price = sel.xpath(price_xpath).extract()
        _prices = []
        if len(list_price_data) != 0 and len(data_sale_price) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|[$]|Sale')
            price = data_re.sub('', data_sale_price[len(data_sale_price) - 1])
            if(price.find('-') != -1):
                _prices = price.split('-')
                price = _prices[0].strip()
            item['price'] = self._format_price('USD', str(price))
        elif len(data_price) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|[$]|Price')
            price = data_re.sub('', data_price[len(data_price) - 1])
            if(price.find('-') != -1):
                _prices = price.split('-')
                price = _prices[0].strip()
            item['price'] = self._format_price('USD', str(price))

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="original_price"]/text()'
        list_price_data = sel.xpath(list_price_xpath).extract()
        if len(list_price_data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|[:$]|Original Price')
            list_price = data_re.sub('', \
                list_price_data[len(list_price_data) - 1])
            item['list_price'] = self._format_price('USD', str(list_price))

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
        url = sel.response.url
        indx1 = url.find("PRD~") + len("PRD~")
        indx2 = url.find("/", indx1)
        id = ''
        if indx2 != -1:
            id = url[indx1:indx2]
        else:
            id = url[indx1:]
        review_url = 'http://belk.ugc.bazaarvoice.com/8131-en_us/idnum/reviews.djs?format=embeddedhtml'
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

    def _get_image(self, image_url):
        idx1 = image_url.rfind('layer=comp&&$P_SWATCH$');
        idx2 = image_url.rfind('layer=comp&$P_SWATCH$');
        idx3 = image_url.rfind('layer=comp&$P_PROD_NEW$')
        if(image_url.find('http:') == -1):
            if(idx1 != -1):
                image_url = image_url[:idx1]
                image_url = image_url.join(["http:",
                    "$PROD_DETAIL_ZOOM$"])
            if(idx2 != -1):
                image_url = image_url[:idx2]
                image_url = image_url.join(["http:",
                    "$PROD_DETAIL_ZOOM$"])
            if(idx3 != -1):
                image_url = image_url[:idx3]
                image_url = image_url.join(["http:",
                    "$PROD_DETAIL_ZOOM$"])
        else:
            if(idx1 != -1):
                image_url = image_url.replace(
                    'layer=comp&&$P_SWATCH$', "$PROD_DETAIL_ZOOM$")
            if(idx2 != -1):
                image_url = image_url.replace(
                    'layer=comp&$P_SWATCH$', "$PROD_DETAIL_ZOOM$")
            if(idx3 != -1):
                image_url = image_url.replace(
                    'layer=comp&$P_PROD_NEW$', "$PROD_DETAIL_ZOOM$")
        return image_url
def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
