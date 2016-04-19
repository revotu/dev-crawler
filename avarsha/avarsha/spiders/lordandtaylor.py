# -*- coding: utf-8 -*-
# author: tanyafeng

import re
import urllib2
import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'lordandtaylor'

class LordandtaylorSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["lordandtaylor.com"]
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(LordandtaylorSpider, self).__init__(*args, **kwargs)

        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        requests = []
        item_pattern = re.compile('\\("(.*)"')
        for line in sel.response.body.split('\n'):
            if line.find('setCatEntryDisplayURL') != -1:
                match = item_pattern.findall(line)
                if len(match) != 0:
                    item_urls.append(match[0])
                    requests.append(scrapy.Request(match[0], \
                                                   callback=self.parse_item))
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        total_count = 0
        begin_index = 1
        requests = []
        total_pattern = re.compile('totalCount\\W*(\\d*)')
        index_pattern = re.compile('beginIndex=(\\d*)')
        match = index_pattern.findall(sel.response.url)
        if (len(match) == 0) or (match[0] == '0'):
            begin_index = 100
        else:
            begin_index = int(match[0]) + 100

        for line in sel.response.body.split('\n'):
            if line.find('totalCount') != -1:
                match = total_pattern.findall(line)
                total_count = int(match[0])
                break

        if begin_index > total_count:
            return []
        else:
            base_url_pattern = re.compile('goToResultPage\\(\'(.*?)\',')
            replace_pattern = re.compile('beginIndex=\\d*')
            for line in sel.response.body.split('\n'):
                if line.find('href="javaScript:;" ') != -1:
                    match = base_url_pattern.findall(line)
                    base_url = match[0].replace('&amp;', '&')
                    next_url = replace_pattern.sub('beginIndex=%d' \
                        % begin_index, base_url)
                    list_urls.append(next_url)
                    requests.append(scrapy.Request(next_url, \
                        callback=self.parse))
                    break
            return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@property="og:title"]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Lordandtaylor'

    def _extract_brand_name(self, sel, item):
        brand_pattern = re.compile('"brand".*?"(.*)"')
        for line in sel.response.body.split('\n'):
            if line.find('"brand":') != -1:
                match = brand_pattern.findall(line)
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
        description_xpath = '//*[@id="detial_main_content"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_urls = []
        img_id_pattern = re.compile('"ItemThumbUPC".*?"(.*)"')
        img_url_pattern = re.compile('\\sdojo\\.attr.*"(//.*)"\\)')
        replace_pattern = re.compile('LordandTaylor/.*?_')
        multi_img_ids = []
        for line in sel.response.body.split('\n'):
            if line.find('"ItemThumbUPC"') != -1:
                match = img_id_pattern.findall(line)
                multi_img_ids.append(match[0])
        img_ids = list(set(multi_img_ids))
        match = img_url_pattern.findall(sel.response.body)
        n = len(match)
        for i in range(0, n - 2):
            tmp_urls = match[i].split('$')
            base_img_url = 'http:' + tmp_urls[0] + \
                '$PDPLARGE$&wid=970&hei=1245&fit=fit,1'
            for img_id in img_ids:
                img_url = replace_pattern.sub('LordandTaylor/%s_' % img_id, \
                    base_img_url)
                img_urls.append(img_url)
        item['image_urls'] = img_urls


    def _extract_colors(self, sel, item):
        color_xpath = '//*[@class="color_swatch_list"]/ul/li/a/img/@alt'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//*[@class="detail_size"]/li/a/@title'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_pattern = re.compile('"\\$(.*)"')
        for line in sel.response.body.split('\n'):
            if line.find('offerPrice') != -1:
                match = price_pattern.findall(line)
                item['price'] = 'USD ' + match[0]
                break

    def _extract_list_price(self, sel, item):
        list_price_pattern = re.compile('"\\$(.*)"')
        for line in sel.response.body.split('\n'):
            if line.find('listPrice') != -1:
                match = list_price_pattern.findall(line)
                item['list_price'] = 'USD ' + match[0]
                break

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
        review_rating = 0
        review_list = []
        item['max_review_rating'] = 5
        pcode_xpath = '//input[@name="sku"]/@value'
        data = sel.xpath(pcode_xpath).extract()
        data[0] = data[0].replace('-', '__')
        key_str = self.__encrypt(data[0].strip())
        head_str = 'http://www.lordandtaylor.com/wcsstore/Lord%20and%20Taylor/pwr/content/'
        tail1_str = '-en_US-'
        tail2_str = '-reviews.js'
        des_url = head_str + key_str + '/' + data[0].strip() + tail1_str + str(1) + tail2_str
        request = urllib2.Request(des_url)
        temp_count = 0
        pagenum = 1
        review_rating_sum = 0.0
        while True:
            try :
                content = urllib2.urlopen(request).read()
            except Exception, e:
                print e
                break
            else :
                tmp_review_count = content.count('{r:{')
                if tmp_review_count == 0:
                    break
                else:
                    temp_count += tmp_review_count
                    print 'count', temp_count
                    indx = content.find('{r:{')
                    while indx != -1:
                        indx1 = content.find(',r:', indx + len('{r:{')) + len(',r:')
                        indx2 = content.find(',', indx1)
                        rating = float(content[indx1:indx2])
                        indx1 = content.find(',db:"', indx + len('{r:{')) + len(',db:"')
                        indx2 = content.find('"', indx1)
                        date = content[indx1:indx2]
                        indx1 = content.find(',n:"', indx + len('{r:{')) + len(',n:"')
                        indx2 = content.find('"', indx1)
                        name = content[indx1:indx2]
                        indx1 = content.find(',h:"', indx + len('{r:{')) + len(',h:"')
                        indx2 = content.find('"', indx1)
                        title = content[indx1:indx2]
                        indx1 = content.find(',p:"', indx + len('{r:{')) + len(',p:"')
                        indx2 = content.find('"', indx1)
                        conts = content[indx1:indx2]
                        review_rating_sum += rating
                        review_list.append({'rating':rating,
                            'date':date,
                            'name':name,
                            'title':title,
                            'content':conts})
                        indx = content.find('{r:{', indx + len('{r:{'))
                        print indx
            pagenum += 1
            des_url = head_str + key_str + '/' + data[0].strip() + tail1_str + str(pagenum) + tail2_str
            request = urllib2.Request(des_url)
        if temp_count == 0:
            item['review_count'] = 0
            return []
        else:
            item['review_count'] = temp_count
            item['review_rating'] = review_rating_sum / temp_count
            item['review_list'] = review_list


    def __encrypt(self, productId):
        sum = 0
        for i in range(len(productId)):
            charnum = ord(productId[i])
            charnum = charnum * abs(255 - charnum)
            sum += charnum
        sum = sum % 1023
        str2 = str(sum)
        for i in range(4 - len(str2)):
            str2 = '0' + str2
        result = str2[0:2] + '/' + str2[2:4]
        return result

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
