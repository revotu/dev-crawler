# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re
import cookielib
import socket
import urllib2
import base64
import time
import types

import scrapy.cmdline
from scrapy import log
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'neimanmarcus'

class NeimanmarcusSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["neimanmarcus.com"]
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(NeimanmarcusSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def convert_url(self, url):
        if(url.find('#') != -1):
            __str = self.__build_str(url)
            base_url = 'http://www.neimanmarcus.com/category.service'
            now = time.time()
            data_final_encoded = base64.b64encode(__str)
            url = ''.join([base_url, '?data=$b64$', data_final_encoded,
                '&service=getCategoryGrid&timestamp=', str(now)])
        elif(url.find('brSearch.jsp?from=brSearch') != -1):
            idx1 = url.find('&q')
            idx2 = url.find('&l', idx1)
            idx3 = url.find('&fl=flags', idx2 + len('&l'))
            url1 = url[:idx1 + len('&q')]
            url2 = url[idx3:]
            new_part = (url[idx1 + len('&q'):idx2]
                .replace('&', '%26').replace(' ', '%20')
                .replace('/', '%2F').replace('[]', '%5B%5D'))
            url = (url1 + new_part + '&l' + new_part + url2)
            url = url.replace(',', '%2C')
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        _url = sel.response.url
        if(_url.find('$b64$') != -1):
            base_url_xpath = '//link[@rel="canonical"]/@href'
            base_url = sel.xpath(base_url_xpath).extract()
            requests = self.__yield_items_request(
                sel, base_url, _url, requests, item_urls)
        elif(_url.find('brSearch.jsp?from=brSearch') != -1):
            base_url = ''
            items_xpath = ('//a[@class="recordTextLink"]/@href')
            requests = self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)
        else:
            base_url = 'http://www.neimanmarcus.com'
            items_xpath = ('//div[@class="category-page"]//div[@class='
                '"productname hasdesigner OneLinkNoTx"]/a/@href')
            requests = self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        _url = sel.response.url
        if(_url.find('$b64$') != -1):
            requests = self._get_b64_next_page(_url, requests, sel, list_urls)
        elif(_url.find('brSearch.jsp?from=brSearch') != -1):
            list_url, start_num, pages = \
                self._get_search_next_page(_url, requests, sel)
            if(start_num > pages * 30):
                return requests
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        else:
            requests = self._get_common_next_page(requests, sel, list_urls)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@class="product-displayname"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
            item['title'] = data_re.sub('' , data[0])

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Neimanmarcus'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//a[@itemprop="brand"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//p[@class="product-sku"]/text()'
        sku2_xpath = '//input[@id="cmos_item"]/@value'
        data = sel.xpath(sku_xpath).extract()
        data2 = sel.xpath(sku2_xpath).extract()
        if len(data) != 0:
            idx1 = data[0].find('sku #')
            idx2 = data[0].find('.', idx1)
            item['sku'] = str(data[0][idx1 + len('sku #'):idx2])
        elif(len(data2) != 0):
            item['sku'] = str(data2[0])

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@itemprop="description"]//*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_url_xpath = ('//div[@class="images"]//ul'
            '[@class="list-inline"]//li/img[@class="product-thumbnail"]/@src')
        img_url_xpath = '//div[@id="prod-img"]/img/@src'
        img_url2_xpath = '//div[@class="img-wrap"]/img/@data-zoom-url'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        data_img = sel.xpath(img_url_xpath).extract()
        data_img2 = sel.xpath(img_url2_xpath).extract()
        if len(data_imgs) != 0:
            for img in data_imgs:
                imgs = self.__extract_img_url(img, imgs)
        elif len(data_img) != 0:
            for img in data_img:
                imgs = self.__extract_img_url(img, imgs)
        elif len(data_img2) != 0:
            imgs = self.__extract_img_url(data_img2[0], imgs)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        product_final_url = self.__pre_process_color_size(sel.response)
        content = self.__construct_XHR(product_final_url)
        color_list_set = set()
        color_content = self.__remove_escape(content)
        while(True):
            idx1 = color_content.find('skus')
            idx2 = color_content.find('productId', idx1 + len('skus'))
            __content = color_content[idx1:idx2]
            if(idx1 == -1): break
            if(item.get('title') is not None):
                if(__content.find(item.get('title')) != -1):
                    break
                else:
                    color_content = color_content[idx2:]
            else:
                log.msg("item.get('title') is None", log.DEBUG)
                break
        while(True):
            idx1 = __content.find('"color":"')
            if idx1 != -1:
                idx2 = __content.find('?', idx1)
                color = __content[idx1 + len('"color":"'):idx2].strip()
                color_list_set.add(color)
                __content = __content[idx2:]
            else:
                break
        item['colors'] = list(color_list_set)

    def _extract_sizes(self, sel, item):
        product_final_url = self.__pre_process_color_size(sel.response)
        content = self.__construct_XHR(product_final_url)
        size_list_set = set()
        size_content = self.__remove_escape(content)
        while(True):
            idx1 = size_content.find('skus')
            idx2 = size_content.find('productId', idx1 + len('skus'))
            __content = size_content[idx1:idx2]
            if(idx1 == -1): break
            if(item.get('title') is not None):
                if(__content.find(item.get('title')) != -1):
                    break
                else:
                    size_content = size_content[idx2:]
            else:
                log.msg("item.get('title') is None", log.DEBUG)
                break
        while(True):
            idx1 = __content.find('"size":"')
            if idx1 != -1:
                idx2 = __content.find('",', idx1)
                size = __content[idx1 + len('"size":"'):idx2].strip()
                size_list_set.add(size)
                __content = __content[idx2:]
            else:
                break
        size_list = list(size_list_set)
        item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price1_xpath = '//p[@class="lbl_ItemPriceSingleItem"]/text()'
        price2_xpath = '//span[@class="pos1override item-price"]/text()'
        data1 = sel.xpath(price1_xpath).extract()
        data2 = sel.xpath(price2_xpath).extract()
        if(len(data1) != 0):
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]')
            _price = data_re.sub('', data1[0])
            item['price'] = self._format_price('USD', str(_price))
        elif(len(data2) != 0):
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|["$]')
            _price = data_re.sub('', data2[0])
            item['price'] = self._format_price('USD', str(_price))

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="item-price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if(len(data) != 0):
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]')
            _list_price = data_re.sub('', data[0])
            item['list_price'] = self._format_price('USD', str(_list_price))

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        free_shipping_xpath = '//div[@class="free"]//b/text()'
        data = sel.xpath(free_shipping_xpath).extract()
        if len(data) != 0 and data[0] == 'FREE':
            item['is_free_shipping'] = True

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass

    def __remove_escape(self, content):
        content = content.replace('\\"', '"')
        content = content.replace('\\', '')
        return content

    def __build_str(self, url):
        arg1 = ('{"GenericSearchReq":{"pageOffset":0'
            ',"pageSize":"30","refinements":"')
        arg2 = '","sort":"PCS_SORT","definitionPath":"'
        arg3 = '","userConstrainedResults":"true","rwd":"true",\
            "advancedFilterReqItems":{"StoreLocationFilterReq":[{\
            "locationInput":"'
        arg4 = '","radiusInput":"'
        arg5 = '","allStoresInput":"'
        arg6 = '","onlineOnly":"'
        arg7 = '"}]},"categoryId":"'
        arg8 = '","sortByFavorites":false,"isFeaturedSort":false,\
            "prevSort":""}}'
        __url = url.split('#')
        __var = __url[1].split('&')
        for line in __var:
            __var_temp = line.split('=')
            if(__var_temp[0] == 'refinements'):
                refinements = __var_temp[1]
            elif(__var_temp[0] == 'definitionPath'):
                definitionPath = __var_temp[1]
            elif(__var_temp[0] == 'catalogId'):
                catalogId = __var_temp[1]
            elif(__var_temp[0] == 'locationInput'):
                locationInput = __var_temp[1].replace('+', '')
            elif(__var_temp[0] == 'radiusInput'):
                radiusInput = __var_temp[1]
            elif(__var_temp[0] == 'allStoresInput'):
                allStoresInput = __var_temp[1]
            elif(__var_temp[0] == 'onlineOnly'):
                onlineOnly = __var_temp[1]
        __str = ''.join([arg1, str(refinements), arg2, str(definitionPath),
            arg3, str(locationInput), arg4, str(radiusInput), arg5,
            str(allStoresInput), arg6, str(onlineOnly), arg7,
            str(catalogId), arg8])
        return __str

    def __pre_process1(self, sel):
        base_url_xpath = '//link[@rel="canonical"]/@href'
        base_url = sel.xpath(base_url_xpath).extract()
        next_pages_xpath = ('//ul[@class="epaging pagination"]//'
            'li[@class="pageOffset"]/@pagenum')
        next_pages = sel.xpath(next_pages_xpath).extract()
        pageOffset = 0
        if(len(next_pages) != 0):
            pageOffset = int(next_pages[len(next_pages) - 1])
        categoryId = ''
        for line in sel.response.body.split('\n'):
            idx1 = line.find('categoryId="')
            if idx1 != -1:
                idx2 = line.find('"', idx1 + len('categoryId="'))
                categoryId = line[idx1 + len('categoryId="') : idx2].strip()
                break
        return base_url, pageOffset, categoryId

    def __pre_process2(self, index, categoryId, sel):
        data_str1 = '{"GenericSearchReq":{"pageOffset":'
        data_str2 = (',"pageSize":"30","refinements":"","sort":"PCS_SORT",'
            '"definitionPath":"/nm/commerce/pagedef_rwd/template/'
            'EndecaDrivenCM","userConstrainedResults":"true","rwd":"true",'
            '"advancedFilterReqItems":{"StoreLocationFilterReq":'
            '[{"locationInput":"","radiusInput":"100","allStoresInput"'
            ':"false","onlineOnly":""}]},"categoryId":"')
        data_str3 = ('","sortByFavorites":false,"isFeaturedSort":'
            'false,"prevSort":""}}')
        next_page_base_url = 'http://www.neimanmarcus.com/category.service'
        index_str = str(index)
        data_final = index_str.join([data_str1, data_str2])
        data_final = categoryId.join([data_final, data_str3])
        data_final_encoded = base64.b64encode(data_final)
        now = time.time()
        params_next_page_url = ''.join([next_page_base_url, \
            '?data=$b64$', data_final_encoded, \
             '&service=getCategoryGrid&timestamp=', str(now)])
        cookie = sel.response.headers.get('Set-Cookie')
        req2 = urllib2.Request(params_next_page_url)
        req2.add_header('Host', 'www.neimanmarcus.com')
        req2.add_header('User-Agent', \
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/'
            '537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 '
            'Safari/537.36')
        req2.add_header('cookie', cookie)
        response = urllib2.urlopen(req2)
        return response

    def _get_b64_next_page(self, _url, requests, sel, list_urls):
        url = _url.split('$b64$')
        new_url = url[1]
        url = new_url.split('&')
        new_url = url[0]
        _base_url = 'http://www.neimanmarcus.com/category.service'
        now = time.time()
        data_decoded = base64.decodestring(new_url)
        content = self.__return_content(sel, _url)
        idx1 = content.find('totalPages":')
        idx2 = content.find(',"', idx1 + len('totalPages":'))
        totalPages = content[idx1 + len('totalPages":'):idx2]
        for index in range(1, int(totalPages)):
            data_re = re.compile(r'pageOffset":\d')
            __str = data_re.sub('pageOffset":' + str(index), data_decoded)
            data_encoded = base64.b64encode(__str)
            new_url = ''.join([_base_url, '?data=$b64$', data_encoded,
                '&service=getCategoryGrid&timestamp=', str(now)])
            base_url_xpath = '//link[@rel="canonical"]/@href'
            base_url = sel.xpath(base_url_xpath).extract()
            requests = self.__yield_items_request(
                sel, base_url, new_url, requests, list_urls)
        return requests

    def _get_search_next_page(self, _url, requests, sel):
        numItems_xpath = '//span[@id="numItems"]/text()'
        data = sel.xpath(numItems_xpath).extract()
        numItems = 0
        if len(data) != 0:
            numItems = int(data[0])
        pages = numItems / 30
        if(numItems % 30 != 0):
            pages += 1
        start_num = 0
        list_url = ''
        idx = _url.find('&start=')
        if(idx != -1):
            idx2 = _url.find('&rows=30', idx)
            pre_start_num = _url[idx + len('&start='):idx2]
            start_num = int(pre_start_num) + 30
            list_url = (
                _url[:idx + len('&start=')] + str(start_num) + _url[idx2:])
        else:
            url1 = ('http://www.neimanmarcus.com/brSearch.jsp'
                '?from=brSearch&fl=flags,merchant_api_json,alt_thumb_image,url'
                '&responsive=true&request_type=search&search_type=keyword')
            url2 = '&fq=&sort=&start='
            url3 = '&rows=30'
            query_part = ''
            idx1 = _url.find('&q=')
            if(idx1 != -1):
                idx2 = _url.find('&l=', idx1)
                idx3 = _url.find('&fl=flags', idx2)
                idx4 = _url.find('&src=suggest', idx2 + len('&l'))
                if(idx4 == -1):
                    query_part = _url[idx1:idx3]
                else:
                    query_part = _url[idx1:idx4]
            start_num = 30
            list_url = url1 + query_part + url2 + str(start_num) + url3
        return list_url, start_num, pages

    def _get_common_next_page(self, requests, sel, list_urls):
        base_url, pageOffset, categoryId = self.__pre_process1(sel)
        if pageOffset != 0:
            for index in range(1, pageOffset):
                response = self.__pre_process2(index, categoryId, sel)
                _count, content = self.__try_read_content(response)
                if _count == 3: continue
                content = self.__remove_escape(content)
                requests = self.__yield_request(
                        base_url, content, requests, list_urls)
        return requests

    def __try_read_content(self, response):
        _count = 0
        content = ''
        while True:
            try:
                content = response.read()
            except :
                log.msg("Error: can\'t read data or IncompleteRead.", log.DEBUG)
                if _count == 3:
                    log.msg("Has tried 3 times. Give up.", log.DEBUG)
                    break
                _count = _count + 1
                continue
            else:
                break
        return _count, content

    def __yield_request(self, base_url, content, requests, item_urls):
        if type(base_url) is types.ListType and len(base_url) == 0:
            base_url = 'http://www.neimanmarcus.com'
        else:
            base_url = base_url[0]
        count = 0
        while True:
            idx1 = content.find('href="/')
            if idx1 != -1:
                count = count + 1
                if count == 3:
                    count = 0
                    idx2 = content.find('">', idx1)
                    product_item_url = ''.join([base_url, \
                        content[idx1 + len('href="/') \
                        - 1 : idx2].strip()])
                    requests.append(scrapy.Request(product_item_url, \
                        callback=self.parse_item))
                    item_urls.append(product_item_url)
                content = content[idx1 + len('href="/'):]
            else: break
        return requests

    def __pre_process_color_size(self, response):
        product_head_url = ('http://www.neimanmarcus.com/'
            'product.service?data=$b64$')
        product_body1_url = ('{"ProductSizeAndColor":{"productIds":"')
        product_body2_url = ('"}}')
        flag = False
        product_ids = set()
        for line in response.body.split('\n'):
            idx1 = line.find('data-product-id="')
            if idx1 != -1:
                idx2 = line.find('"', idx1 + len('data-product-id="'))
                if flag == False:
                    product_id_first = \
                        line[idx1 + len('data-product-id="'):idx2]
                    product_ids.add(product_id_first)
                    flag = True
                else:
                    product_id_temp = line[idx1 + len('data-product-id="'):idx2]
                    product_ids.add(product_id_temp)
        if len(product_ids) > 1:
            product_ids.remove(product_id_first)
        product_body_ids = ','.join(str(v) for v in list(product_ids))
        product_url = ''.join([product_body1_url,
            product_body_ids, product_body2_url])
        product_encoded_url = base64.b64encode(product_url)
        product_final_url = ''.join([product_head_url, product_encoded_url])

        return product_final_url

    def __extract_img_url(self, img, imgs):
        if(img.find('wid=75&height=94') != -1):
            img = 'http:' + img.replace('wid=75&height=94',
                'wid=1200&height=1500')
        elif(img[0] == '/'):
            img = 'http://www.neimanmarcus.com' + img
            img = 'z'.join([img[0 : len(img) - 5], img[len(img) - 4 :]])
        else:
            img = 'z'.join([img[0 : len(img) - 5], img[len(img) - 4 :]])
        imgs.append(img)
        return imgs

    def __construct_XHR(self, product_final_url):
        http_header = {\
                "User-Agent" :\
                ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML,"
                    " like Gecko) Chrome/17.0.963.46 Safari/535.11"), \
                "Accept" :\
                ("text/xml,application/xml,application/xhtml+xml,text/"
                    "html;q=0.9,text/plain;q=0.8,text/png,*/*;q=0.5"), \
                "Accept-Language" :\
                "en-us,en;q=0.5", \
                "Accept-Charset" : "ISO-8859-1", \
                "Content-type": "application/json; charset=UTF-8", \
                }
        params = ''
        timeout = 15
        socket.setdefaulttimeout(timeout)
        cookie_jar = cookielib.LWPCookieJar()
        cookie = urllib2.HTTPCookieProcessor(cookie_jar)
        opener = urllib2.build_opener(cookie)
        req = urllib2.Request(product_final_url, params, http_header)
        res = opener.open(req)
        _count, content = self.__try_read_content(res)

        return content

    def __return_content(self, sel, url):
        cookie = sel.response.headers.get('Set-Cookie')
        req2 = urllib2.Request(url)
        req2.add_header('Host', 'www.neimanmarcus.com')
        req2.add_header('User-Agent', \
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/'
            '537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 '
            'Safari/537.36')
        req2.add_header('cookie', cookie)
        response = urllib2.urlopen(req2)
        _count, content = self.__try_read_content(response)
        content = self._remove_escape(content)
        return content

    def __yield_items_request(self, sel, base_url, url, requests, item_urls):
        content = self.__return_content(sel, url)
        requests = self.__yield_request(base_url, content, requests, item_urls)
        return requests

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
