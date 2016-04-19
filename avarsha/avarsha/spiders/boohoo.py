# -*- coding: utf-8 -*-
# @author: fsp

import urllib
import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'boohoo'

class BoohooSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["boohoo.com", "locayta.com"]

    def __init__(self, *args, **kwargs):
        super(BoohooSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        if url.find('search?') != -1:
            url_head = ('http://esp2.locayta.com/zones-js.aspx?version=2.16.2'
                '&siteId=f018c559-e54e-40a0-b6fe-19797af4d1e0'
                '&UID=6ccca93b-f748-1f7e-402c-a39246637d8a'
                '&SID=631edbe0-d584-1335-f984-54005ca50402'
                '&referrer=&sitereferrer=&pageurl=')
            url_key = urllib.quote(url, '')
            url_tail = ('&zone0=search&tracking=201-1022-7607&facetmode=data'
                '&mergehash=true&searchoperator=AND&currency=USD'
                '&config_categorytree=dev&config_category=dev'
                '&config_parentcategorytree=&config_parentcategory=undefined'
                '&config_accessoryskus=&config_currency=USD'
                '&config_image_size=large'
                '&config_fsm_sid=41cec21e-aefe-da8b-19de-0d84edd6b9ab'
                '&config_fsm_returnuser=1'
                '&config_fsm_currentvisit=04%2F06%2F2015'
                '&config_fsm_visitcount=26&config_fsm_lastvisit=02%2F06%2F2015')
            return url_head + url_key + url_tail
        else:
            content = urllib2.urlopen(url).read()
            sel = Selector(text=content)
            tags_cattree0_path = '//div[@id="tags_cattree0"]/text()'
            tags_cattree_path = '//div[@id="tags_cattree"]/text()'
            tags_cattree0 = sel.xpath(tags_cattree0_path).extract()
            tags_cattree = sel.xpath(tags_cattree_path).extract()

            new_url = self.__compute_url(url, tags_cattree0, \
                tags_cattree)
            return new_url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.boohoo.com'
        items_xpath = ('//li[@class="prod prod-search-results js-prod"]/form/'
            'div/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="pagnnum"]/a/@data-page'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []

        url = sel.response.url
        test_index = url.find('esp_pg')
        tail_index = url.find('&zone0')

        for path in nexts:
            if test_index != -1:
                list_url = url[:test_index] + 'esp_pg%3D' + path
            else:
                test_index2 = url.find('%23')
                # %23 = '#'  %26 = '&'
                if test_index2 != -1:
                    list_url = url[:tail_index] + '%26esp_pg%3D' + path
                else:
                    list_url = url[:tail_index] + '%23esp_pg%3D' + path
            list_url += url[tail_index:]
            list_urls.append(list_url)
            requests.append(scrapy.Request(list_url, callback=self.parse))
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//meta[@name="twitter:title"]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Boohoo'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Boohoo'

    def _extract_sku(self, sel, item):
        pcode_xpath = '//div[@id="invtref"]/text()'
        data = sel.xpath(pcode_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_description(self, sel, item):
        des_xpath = '//div[@itemprop="description"]/p'
        data = sel.xpath(des_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_image_urls(self, sel, item):
        images_xpath = '//a[@id="zoom1"]/@href'
        images = sel.xpath(images_xpath).extract()
        if len(images) != 0:
            item['image_urls'] = images

    def _extract_colors(self, sel, item):
        color_xpath = ('//div[@class="row thinpad-top js-attribute-color"]//'
            'option[not(@value="")]/text()')
        data = sel.xpath(color_xpath).extract()
        color_list = []
        if len(data) != 0:
            for line in data:
                color_list.append(line)
            item['colors'] = color_list

    def _extract_sizes(self, sel, item):
        size_list = []
        size_xpath = ('//div[@class="row thinpad-top js-attribute-size"]'
            '//option[not(@value="")]/text()')
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            for line in data:
                size_list.append(line)
            item['sizes'] = size_list

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="js-attrFeedback js-attributesPrice left"]'
            '//span[@class="prod-price js-prod-price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', \
                (data[0].strip())[len('$'):])

    def _extract_reviews(self, sel, item):
        review_count = 0
        review_rating = 0.0
        review_list = []

        pcode_xpath = '//div[@id="invtref"]/text()'
        data = sel.xpath(pcode_xpath).extract()
        key_str = self.__encrypt(data[0].strip())
        head_str = 'http://www.boohoo.com/partners/pwr/content/'
        tail_str = '-en_GB-1-reviews.js'
        des_url = head_str + key_str + '/' + data[0].strip() + tail_str

        try :
            content = urllib2.urlopen(des_url).read()
        except Exception, e:
            print e
            item['max_review_rating'] = 5
            item['review_count'] = None
            item['review_rating'] = None
            item['review_list'] = None
        else :
            review_count = content.count(',r:')
            pre_index = 0

            review_rating_sum = 0.0

            for j in range(review_count):
                rating_index = content.find(',r:', pre_index)
                rating = int(content[rating_index + len(',r:')])

                review_rating_sum += rating

                title_index = content.find(',h:', rating_index)
                title_index2 = content.find('\"', title_index + len(',h:\"') + 1)
                title = content[title_index + len(',h:\"'):title_index2]

                name_index = content.find(',n:', title_index)
                name_index2 = content.find('\"', name_index + len(',n:\"') + 1)
                name = content[name_index + len(',n:\"'):name_index2]

                date_index = content.find(',d:', name_index2)
                date_index2 = content.find('\"', date_index + len(',d:\"') + 1)
                date = content[date_index + len(',d:\"'):date_index2]
                date = date.replace('\\/', '/')

                reviews_index = content.find(',p:', name_index)
                reviews_index2 = content.find('\"', reviews_index\
                    + len(',p:\"') + 1)
                reviews = content[reviews_index + len(',p:\"'):reviews_index2]

                pre_index = reviews_index2

                review_list.append({'rating':rating,
                    'date':date,
                    'name':name,
                    'title':title,
                    'content':reviews})

                review_rating = review_rating_sum / review_count
            item['max_review_rating'] = 5
            item['review_count'] = review_count
            item['review_rating'] = review_rating
            item['review_list'] = review_list

    def __remove_escape(self, content):
        content = content.replace('\\\"', '"')
        content = content.replace('\\n', '')
        content = content.replace('\\/', '/')
        content = content.replace('\"', '"')
        content = content.replace('\/', '/')
        return content

    def __encrypt(self, product_id):
        sum = 0
        for i in range(len(product_id)):
            charnum = ord(product_id[i])
            charnum = charnum * abs(255 - charnum)
            sum += charnum
        sum = sum % 1023
        str2 = str(sum)
        for i in range(4 - len(str2)):
            str2 = '0' + str2
        result = str2[0:2] + '/' + str2[2:4]
        return result

    def __compute_url(self, url, tags_cattree0, tags_cattree):
        head_url = ('http://esp2.locayta.com/zones-js.aspx?'
            'version=2.16.2&siteId=f018c559-e54e-40a0-b6fe-19797af4d1e0&'
            'UID=6ccca93b-f748-1f7e-402c-a39246637d8a&'
            'SID=3b2e0877-3d6a-61e0-5f25-1ad352d769c3&'
            'referrer=&'
            'sitereferrer=&pageurl=')
        if url.find('search') != -1:
            tail_url1 = '&zone0=search'
        else:
            tail_url1 = '&zone0=prod_list_prods'
        tail_url1 += '&facetmode=data&mergehash=true&currency=USD&'

        if tags_cattree[0].strip(',').strip(',') == '':
            categorytree = tags_cattree0[0]
        else:
            categorytree = tags_cattree0[0] + ',' + tags_cattree[0].strip(',')

        category_index = categorytree.rfind(',')
        parentcategory_index = categorytree.find(',')
        if category_index != -1:
            category = categorytree[category_index + len(','):]
        else:
            category = categorytree

        tail_url2 = 'config_categorytree=' + categorytree.replace(',', '%2F')
        tail_url2 += '&config_category=' + category
        tail_url2 += '&config_parentcategorytree=' + \
            categorytree[ :category_index].replace(',', '%2F')
        if parentcategory_index != -1:
            tail_url2 += '&config_parentcategory=' + \
                categorytree[parentcategory_index + len(',') : category_index]
        else:
            tail_url2 += '&config_parentcategory=undefined'
        tail_url2 += ('&config_icxtcore=&config_accessoryskus='
            '&config_image_size=large'
            '&config_currency=USD'
            '&config_fsm_sid=3b2e0877-3d6a-61e0-5f25-1ad352d769c3'
            '&config_fsm_returnuser=1'
            '&config_fsm_currentvisit=02%2F04%2F2015'
            '&config_fsm_visitcount=7'
            '&config_fsm_lastvisit=01%2F04%2F2015')

        url = head_url + urllib.quote(url, '') + tail_url1 + tail_url2
        return url

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
