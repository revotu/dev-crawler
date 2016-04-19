# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline
import urllib2
from sets import Set

from avarsha_spider import AvarshaSpider


_spider_name = 'jcpenney'

class JcpenneySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["jcpenney.com"]

    def __init__(self, *args, **kwargs):
        super(JcpenneySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.jcpenney.com'
        items_xpath = (
            '//*[@class="product_gallery_holder2"]//a[@onclick='
            '"trackPageLoadTime(\'Clicked_On_PP_In_Gallery\');"]/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.jcpenney.com'
        nexts_xpath = '//*[@id="paginationIdBOTTOM"]//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            idx1 = data[0].find(u'\xae')
            if idx1 != -1:
                item['title'] = data[0][idx1 + 1:].strip()
            else:
                item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Jcpenney'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            idx1 = data[0].find(u'\xae')
            if idx1 != -1:
                item['brand_name'] = data[0][:idx1].strip()
        else:
            item['brand_name'] = 'Jcpenney'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@id="productWebId"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][len('web ID: '):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@itemprop="description"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        mark_start = 'var imageName = "'
        for line in sel.response.body.split('\n'):
            idx1 = line.find(mark_start)
            if idx1 != -1:
                idx2 = line.find('";', idx1)
                img_names = list(
                    Set(line[idx1 + len(mark_start):idx2].split(',')))
                for img_name in img_names:
                    img_url = ('http://s7d2.scene7.com/is/image/JCPenney/'
                        + img_name
                        + '?id=TmLpQ0&scl=1.3333333333333333'
                        '&req=tile&rect=0,0,1500,1500&fmt=jpg')
                    imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_list_xpath = '//*[@class="small_swatches"]/li'
        data = sel.xpath(color_list_xpath)
        color_list = []
        for li in data:
            color_list.append(
                (li.xpath('.//div/p/text()').extract()[0]).strip())
        if len(color_list) != 0:
            item['colors'] = color_list

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//*[@id="size"]/a/text()'
        not_available_size_list_xpath = '//*[@class="sku_not_available"]/a/text()'
        data1 = sel.xpath(size_list_xpath).extract()
        data2 = sel.xpath(not_available_size_list_xpath).extract()
        size_list = []
        for size in data1:
            if size not in data2:
                size_list.append(size)
        if len(size_list) != 0:
            item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/a/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) == 0:
            price_xpath = '//span[@itemprop="price"]/text()'
            data = sel.xpath(price_xpath).extract()
        price = data[0].strip()\
            .replace('sale', '')\
            .replace('clearance', '')
        price_num = price.strip()[len('$'):]
        item['price'] = self._format_price('USD', price_num)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//span[@class="'
                'pp_page_price price_normal flt_wdt"]/a/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_str = data[0]
            list_price = list_price_str.replace('original', '')
            price_num = list_price.strip()[len('$'):]
            item['list_price'] = self._format_price('USD', price_num)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        is_free_shipping_xpath = '//*[@id="shipOpts"]/span/text()'
        data = sel.xpath(is_free_shipping_xpath).extract()
        if len(data) != 0 and data[0] == 'Free':
            item['is_free_shipping'] = True

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        product_id_xpath = '//input[@id="favoriteppId"]/@value'
        data = sel.xpath(product_id_xpath).extract()
        id = ''
        if len(data) == 0:
            return []
        else:
            id = data[0]
        review_url = 'http://jcpenney.ugc.bazaarvoice.com/1573-en_us/idnum/reviews.djs?format=embeddedhtml'
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
