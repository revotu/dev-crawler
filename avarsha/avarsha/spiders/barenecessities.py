# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re
import scrapy.cmdline
from avarsha_spider import AvarshaSpider
import urllib2
import json
import math
from scrapy.selector import Selector



_spider_name = 'barenecessities'

class BarenecessitiesSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["barenecessities.com"]

    def __init__(self, *args, **kwargs):
        super(BarenecessitiesSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        items_xpath = '//li[@class="item thumbnail-item"]/a[@class="link-wrap"]/@href'
        item_nodes = sel.xpath(items_xpath).extract()
        print item_nodes
        requests = []
        for path in item_nodes:
            item_url = path
            if(item_url[len(item_url) - 1] == ' '):
                item_url = item_url.strip() + '%20'
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//a[@name="&lid=Next&lpos=sort_by"]/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        _title = ''
        title_xpath = '//span[@class="productNameLbl"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Bare Necessities'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = \
            '//span[@id="ctl00_cphMainContent_vendorLabel"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if(len(data) != 0):
            data_re = re.compile(':')
            _data = data_re.sub('', data[0]).strip()
            item['brand_name'] = _data

    def _extract_sku(self, sel, item):
        url = sel.response.url
        indx1 = url.find("pf_id=") + len("pf_id=")
        indx2 = url.find("&", indx1)
        id = ''
        if indx2 != -1:
            id = url[indx1:indx2]
        else:
            id = url[indx1:]
        item['sku'] = id

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="BulletsPanel"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        colors = []
        _line = ''
        _var1 = 'http://is3.barenecessities.com/is/image/BareNecessities/'
        _var2 = '?$productzoom$'
        colors_xpath = '//img[@data-swatchcolor]/@data-swatchcolor'
        data_colors = sel.xpath(colors_xpath).extract()
        if len(data_colors) != 0:
            colors = data_colors
        for line in sel.response.body.split('\n'):
            if(line.find('BN_PageData = {') != -1):
                _line = line
                break
        while(True):
            idx1 = _line.find('ColorValue": "')
            if(idx1 != -1):
                idx2 = _line.find('",', idx1)
                _color = _line[idx1 + len('ColorValue": "'):idx2]
                if(_color in colors):
                    idx3 = _line.find('ImageName": "', idx2)
                    idx4 = _line.find('" }', idx3)
                    _var = str(_line[idx3 + len('ImageName": "'):idx4])
                    image_url = _var1 + _var + _var2
                    imgs.append(image_url)
                _line = _line[idx2:]
            else:
                break
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@id="spanOurPrice"]/span/text()'
        price2_xpath = '//span[@id="ctl00_cphMainContent_productPricingControl_listPrice"]/text()'
        price3_xpath = '//span[@class="prodColorPrice"]/span/text()'
        price = sel.xpath(price_xpath).extract()
        price2 = sel.xpath(price2_xpath).extract()
        price3 = sel.xpath(price3_xpath).extract()
        if len(price) != 0:
            price[0] = price[0].replace(' ', "")
            indx = price[0].find('(')
            if indx != -1:
                price_number = price[0][len('$'):indx].strip()
            else:
                price_number = price[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)
        elif len(price3) != 0:
            price_number = price3[0].replace('$', '')
            item['price'] = self._format_price('USD', price_number)
        else:
            self.log('OUT OF STOCK!')
        if len(price2) != 0:
            price2[0] = price2[0].replace(' ', "")
            price_number = price2[0][len('$'):].strip()
            item['list_price'] = self._format_price('USD', price_number)

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
        url = sel.response.url
        indx1 = url.find("pf_id=") + len("pf_id=")
        indx2 = url.find("&", indx1)
        id = ''
        if indx2 != -1:
            id = url[indx1:indx2]
        else:
            id = url[indx1:]
        review_url = 'http://barenecessities.ugc.bazaarvoice.com/2417-en_us/idnum/reviews.djs?format=embeddedhtml'
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
            while indx != -1:
                indx += len('BVSubmissionPopupContainer')
                indx1 = content.find('BVRRNumber BVRRRatingNumber', indx) + len('BVRRNumber BVRRRatingNumber')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                data = content[indx2:indx3]
                rating = float(data)
                indx1 = content.find('BVRRValue BVRRReviewDate', indx) + len('BVRRValue BVRRReviewDate')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                date = content[indx2:indx3]
                indx1 = content.find('BVRRNickname', indx) + len('BVRRNickname')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                name = content[indx2:indx3]
                indx1 = content.find('BVRRValue BVRRReviewTitle', indx) + len('BVRRValue BVRRReviewTitle')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                title = content[indx2:indx3]
                indx1 = content.find('span class=\\"BVRRReviewText\\"', indx) + len('span class=\\"BVRRReviewText\\"')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('span', indx2)
                cont = content[indx2:indx3 - 2]
                review_list.append({'rating':rating,
                  'date':date,
                  'name':name,
                  'title':title,
                  'content':cont})
                indx = content.find('BVSubmissionPopupContainer', indx)
                review_num += 1
        item['review_list'] = review_list



def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
