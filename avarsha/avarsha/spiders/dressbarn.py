# -*- coding: utf-8 -*-
# @author: wanghaiyi

import scrapy.cmdline
import urllib2
from avarsha_spider import AvarshaSpider


_spider_name = "dressbarn"

class DressbarnSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["dressbarn.com"]

    def __init__(self, *args, **kwargs):
        super(DressbarnSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//a[@class="description"]/@title'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//span[@class="next"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1/span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Dressbarn'

    def _extract_brand_name(self, sel, item):
        data = sel.response.url.replace('http://', '')
        if data.find('-by-') != -1:
            num_tmp = data.find('-by-')
            data = data[data.find('/') + 1:num_tmp]
            item['brand_name'] = data[data.find('/') + 1:]
        else:
            item['brand_name'] = 'Dressbarn'

    def _extract_sku(self, sel, item):
        data = sel.response.url[:sel.response.url.rfind('/')]
        data = data[data.rfind('/') + 1:]
        if len(data) != 0:
            item['sku'] = data

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desc_tmp = ''
        description_xpath = '//div[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                desc_tmp += data[i]
        description_detail_xpath = '//div[@class="details_content"]/ul'
        data = sel.xpath(description_detail_xpath).extract()
        if len(data) != 0:
            for i in range(1 , len(data)):
                desc_tmp += data[i]
        item['description'] = desc_tmp

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_url_list = []
        idx1 = sel.response.body
        idx1 = idx1.replace('\n' , '')
        while idx1.find('\"xlarge\":') != -1:
            idx_num_tmp = idx1.find('\"xlarge\":')
            idx1 = idx1[idx_num_tmp + 11:]
            idx_num2 = idx1.find('front\"')
            idx1 = idx1[idx_num2 + 9:]
            idx_num3 = idx1.find("\"back")
            idx_num4 = idx1.find('swatches')
            if (idx_num4 > idx_num3) | (idx_num4 == -1):
                url_tmp = idx1[:idx_num3 - 2].replace('\\' , '')
                img_url_list.append('http://www.dressbarn.com' + url_tmp)
                idx1 = idx1[idx_num3 + 9:]
                url_tmp = idx1[:idx1.find('jpg') + 3].replace('\\' , '')
                img_url_list.append('http://www.dressbarn.com' + url_tmp)
            else:
                url_tmp = idx1[:idx_num4 - 4].replace('\\' , '')
                img_url_list.append('http://www.dressbarn.com' + url_tmp)
        item['image_urls'] = img_url_list

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div/span[@itemprop="price"]/text()'
        list_price_xpath = '//span[@class="price_range"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            if data[0].find('-') == -1:
                item['price'] = self._format_price('USD', data[0].replace('$', ''))
            else:
                price_tmp = data[0][:data[0].find('-') - 1]
                item['price'] = self._format_price('USD', price_tmp.replace('$', ''))
        else:
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                item['price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_list_price(self, sel, item):
        price_xpath = '//div/span[@itemprop="price"]/text()'
        list_price_xpath = '//span[@class="price_range"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                item['list_price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_low_price(self, sel, item):
        list_price_xpath = '//span[@class="price_range"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            if data[0].find('-') != -1:
                price_tmp = data[0][:data[0].find('-') - 1]
                item['low_price'] = self._format_price('USD', price_tmp.replace('$', ''))

    def _extract_high_price(self, sel, item):
        list_price_xpath = '//span[@class="price_range"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            if data[0].find('-') != -1:
                price_tmp = data[0][data[0].find('-') + 2:]
                item['high_price'] = self._format_price('USD', price_tmp.replace('$', ''))

    def _extract_is_free_shipping(self, sel, item):
        pass
    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        product_id_xpath = '//*[@id="container"]/div/@itemid'
        data = sel.xpath(product_id_xpath).extract()
        print data
        id = ''
        if len(data) == 0:
            return []
        else:
            id = data[0]
        review_url = 'http://reviews.dressbarn.com/6655/idnum/reviews.htm?format=embedded'
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
                indx1 = content.find('span class="BVRRReviewText"', indx)
                if indx1 != -1:
                    indx1 += len('span class="BVRRReviewText"')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('span', indx2)
                    cont = content[indx2:indx3 - 2]
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
