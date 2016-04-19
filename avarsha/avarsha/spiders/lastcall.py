# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re
import urllib2
import base64
import time
import types

import scrapy.cmdline
from scrapy import log
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'lastcall'

class LastcallSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["lastcall.com"]
    is_first = True

    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(LastcallSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def convert_url(self, url):
        if(url.find('#') != -1):
            __str = self.__build_str(url)
            base_url = 'http://www.lastcall.com/category.service'
            now = time.time()
            data_final_encoded = base64.b64encode(__str)
            url = ''.join([base_url, '?data=$b64$', data_final_encoded,
                '&service=getCategoryGrid&timestamp=', str(now)])
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.lastcall.com'
        items_xpath = ('//div[@class="products"]'
            '//a[@class="recordTextLink"]/@href')

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        if(self.is_first == False):
            return requests
        self.is_first = False
        list_url = ''
        if(sel.response.url.find('$b64$') == -1):
            base_url, pageOffset, categoryId = self.__pre_process1(sel)
            if pageOffset != 0:
                for index in range(1, pageOffset):
                    if(categoryId != ''):
                        list_url = self._get_normal_next_page(index, categoryId)
                    else:
                        list_url = self._get_search_next_page(index, sel)
                    list_urls.append(list_url)
                    request = scrapy.Request(list_url, callback=self.parse)
                    requests.append(request)
        else:
            url = sel.response.url.split('$b64$')
            _url = url[1]
            url = _url.split('&')
            _url = url[0]
            __base_url = 'http://www.lastcall.com/category.service'
            now = time.time()
            data_decoded = base64.decodestring(_url)
            content = self.__return_content(sel, sel.response.url)
            idx1 = content.find('totalPages":')
            idx2 = content.find(',"', idx1 + len('totalPages":'))
            totalPages = content[idx1 + len('totalPages":'):idx2]
            for index in range(1, int(totalPages)):
                data_re = re.compile(r'pageOffset":\d')
                __str = data_re.sub('pageOffset":' + str(index), data_decoded)
                data_encoded = base64.b64encode(__str)
                list_url = ''.join([__base_url, '?data=$b64$', data_encoded,
                    '&service=getCategoryGrid&timestamp=', str(now)])
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@id="productDetails"]/h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]')
            title = data_re.sub('', data[len(data) - 1])
            idx = title.rfind(',')
            if idx != -1:
                title = title[:idx]
            item['title'] = title

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Lastcall'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//span[@itemprop="brand"]/a/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'<[^<>]+>|\n+|\r+|\t+| +')
            _brand_name = data_re.sub('', data[0])
            item['brand_name'] = _brand_name

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@id = "MpsShortSku"]/text()'
        sku2_xpath = '//p[@class="GRAY10N OneLinkNoTx"]/text()'
        data = sel.xpath(sku_xpath).extract()
        data2 = sel.xpath(sku2_xpath).extract()
        line = ''
        if len(data) != 0:
            line = data[0]
            idx1 = line.find('sku')
            line = line[idx1:]
            data_re = re.compile(r' +|sku|[#,.]')
            line = data_re.sub('', line)
        elif(len(data2) != 0):
            line = data2[0]
            data_re = re.compile(r'\n+|\t+|\r+| +')
            line = data_re.sub('', line)
        item['sku'] = str(line)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="cutline short "]//*'
        data = sel.xpath(description_xpath).extract()
        if(len(data) != 0):
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_url_xpath = '//div[@class="views"]//img/@src'
        imgs_url2_xpath = '//img[@itemprop="image"]/@data-zoom-url'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        data2_imgs = sel.xpath(imgs_url2_xpath).extract()
        if len(data_imgs) != 0:
            for image_url in data_imgs:
                image_url = image_url.replace('g.jpg', 'z.jpg')
                if(image_url.find('/mg/') != -1):
                    image_url = image_url.replace('/mg/', '/mz/')
                if(image_url.find('/ag/') != -1):
                    image_url = image_url.replace('/ag/', '/az/')
                if(image_url.find('/eg/') != -1):
                    image_url = image_url.replace('/eg/', '/ez/')
                imgs.append(image_url)
        elif len(data2_imgs) != 0:
            imgs.append(data2_imgs[0])
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@itemprop="price"]'
        price2_xpath = '//div[@class="promoPrice pos3"]'
        data = sel.xpath(price_xpath).extract()
        data2 = sel.xpath(price2_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|["$]')
            __price = data_re.sub('', data[0])
            item['price'] = self._format_price('USD', str(__price))
        elif len(data2) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|["$]')
            __price = data_re.sub('', data2[0])
            item['price'] = self._format_price('USD', str(__price))

    def _extract_list_price(self, sel, item):
        list_price_xpath = \
            '//div[@class="lineItemInfo"]//div[@class=\
            "price pos1priceDisplayStyleOverride"]'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|["$]')
            __list_price = data_re.sub('', data[0])
            item['list_price'] = self._format_price('USD', str(__list_price))

    def _extract_low_price(self, sel, item):
        low_price_xpath = \
            '//div[@class="lineItemInfo"]//div[@class="adornmentPriceElement"]'
        data = sel.xpath(low_price_xpath).extract()
        if len(data) != 0:
            for line in data:
                if(line.find('Was:') != -1):
                    idx1 = line.find('$')
                    if(idx1 != -1):
                        idx2 = line.find('</div>', idx1)
                        __low_price = line[idx1 + 1:idx2]
                        item['low_price'] = \
                            self._format_price('USD', str(__low_price))
                    break

    def _extract_high_price(self, sel, item):
        high_price_xpath = \
            '//div[@class="lineItemInfo"]//div[@class="adornmentPriceElement"]'
        data = sel.xpath(high_price_xpath).extract()
        if len(data) != 0:
            for line in data:
                if(line.find('Compare to:') != -1):
                    idx1 = line.find('$')
                    if(idx1 != -1):
                        idx2 = line.find('</div>', idx1)
                        __high_price = line[idx1 + 1:idx2]
                        item['high_price'] = \
                            self._format_price('USD', str(__high_price))
                    break

    def _extract_is_free_shipping(self, sel, item):
        pass

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass

    def __pre_process1(self, sel):
        base_url_xpath = '//link[@rel="canonical"]/@href'
        base_url = sel.xpath(base_url_xpath).extract()
        next_pages_xpath = ('//div[@id="epaging"]'
            '//div[@class="pageOffset"]/text()')
        next_pages = sel.xpath(next_pages_xpath).extract()
        next_pages = map(eval, next_pages)
        pageOffset = 0
        if(len(next_pages) != 0):
            pageOffset = max(next_pages)
        categoryId = ''
        for line in sel.response.body.split('\n'):
            idx1 = line.find('categoryId="')
            if idx1 != -1:
                idx2 = line.find('"', idx1 + len('categoryId="'))
                categoryId = line[idx1 + len('categoryId="') : idx2].strip()
                break
        return base_url, pageOffset, categoryId

    def _get_normal_next_page(self, index, categoryId):
        data_str1 = '{"GenericSearchReq":{"pageOffset":'
        data_str2 = (',"pageSize":"30","refinements":"","sort":"PCS_SORT",'
            '"endecaDrivenSiloRefinements":"fromDrawer=true",'
            '"definitionPath":"/nm/commerce/pagedef/template/EndecaDriven",'
            '"advancedFilterReqItems":{"StoreLocationFilterReq":'
            '[{"locationInput":"","radiusInput":"100","allStoresInput":'
            '"false","onlineOnly":"instore"}]},"categoryId":"')
        data_str3 = ('","sortByFavorites":false,'
            '"isFeaturedSort":false,"prevSort":""}}')
        next_page_base_url = 'http://www.lastcall.com/category.service'
        index_str = str(index)
        data_final = index_str.join([data_str1, data_str2])
        data_final = categoryId.join([data_final, data_str3])
        data_final_encoded = base64.b64encode(data_final)
        now = time.time()
        params_next_page_url = ''.join([next_page_base_url,
            '?data=$b64$', data_final_encoded, \
             '&service=getCategoryGrid&timestamp=', str(now)])

        return params_next_page_url

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
            base_url = 'http://www.lastcall.com'
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
                        content[idx1 + len('href="/') - 1:idx2].strip()])
                    item_urls.append(product_item_url)
                    requests.append(scrapy.Request(product_item_url,
                        callback=self.parse_item))
                content = content[idx1 + len('href="/'):]
            else: break
        return requests

    def __return_content(self, sel, url):
        cookie = sel.response.headers.get('Set-Cookie')
        req2 = urllib2.Request(url)
        req2.add_header('Host', 'www.lastcall.com')
        req2.add_header('User-Agent',
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

    def __build_str(self, url):
        arg1 = ('{"GenericSearchReq":{"pageOffset":0'
            ',"pageSize":"30","refinements":"')
        arg2 = '","sort":"PCS_SORT",'
        arg2_new = '"endecaDrivenSiloRefinements":"fromDrawer=true",'
        arg2_0 = '"definitionPath":"'
        arg3 = ('","userConstrainedResults":"true",'
            '"advancedFilterReqItems":{"StoreLocationFilterReq":[{')
        arg4 = '"locationInput":"'
        arg5 = '"radiusInput":"'
        arg10 = '",'
        arg6 = '"allStoresInput":"'
        arg7 = '","onlineOnly":"'
        arg8 = '"}]},"categoryId":"'
        arg9 = '","sortByFavorites":false,"isFeaturedSort":false,\
            "prevSort":""}}'
        __url = url.split('#')
        __var = __url[1].split('&')
        refinements = ''
        endecaDrivenSiloRefinements = ''
        definitionPath = ''
        locationInput = ''
        radiusInput = ''
        allStoresInput = ''
        onlineOnly = ''
        for line in __var:
            __var_temp = line.split('=')
            if(__var_temp[0] == 'refinements'):
                refinements = __var_temp[1]
            elif(__var_temp[0] == 'endecaDrivenSiloRefinements'):
                endecaDrivenSiloRefinements = __var_temp[1]
            elif(__var_temp[0] == 'definitionPath'):
                definitionPath = __var_temp[1]
            elif(__var_temp[0] == 'locationInput'):
                locationInput = __var_temp[1].replace('+', '')
            elif(__var_temp[0] == 'radiusInput'):
                radiusInput = __var_temp[1]
            elif(__var_temp[0] == 'allStoresInput'):
                allStoresInput = __var_temp[1]
            elif(__var_temp[0] == 'onlineOnly'):
                onlineOnly = __var_temp[1]
        __url = url.split('/c.cat')
        idx1 = __url[0].rfind('/')
        idx2 = __url[0].find('_cat')
        categoryId = __url[0][idx1 + 1:idx2]
        __str = ''
        if(endecaDrivenSiloRefinements != ''):
            if(locationInput != '' and radiusInput != ''):
                __str = ''.join([arg1, str(refinements), arg2, arg2_new, arg2_0,
                    str(definitionPath), arg3, arg4, str(locationInput), arg10,
                    arg5, str(radiusInput), arg10, arg6, str(allStoresInput),
                    arg7, str(onlineOnly), arg8, str(categoryId), arg9])
            else:
                __str = ''.join([arg1, str(refinements), arg2, arg2_new, arg2_0,
                    str(definitionPath), arg3, arg6, str(allStoresInput),
                    arg7, str(onlineOnly), arg8, str(categoryId), arg9])
        else:
            if(locationInput != '' and radiusInput != ''):
                __str = ''.join([arg1, str(refinements), arg2, arg2_0,
                    str(definitionPath), arg3, arg4, str(locationInput), arg10,
                    arg5, str(radiusInput), arg10, arg6, str(allStoresInput),
                    arg7, str(onlineOnly), arg8, str(categoryId), arg9])
            else:
                __str = ''.join([arg1, str(refinements), arg2, arg2_0,
                    str(definitionPath), arg3, arg6, str(allStoresInput),
                    arg7, str(onlineOnly), arg8, str(categoryId), arg9])
        return __str

    def _get_search_next_page(self, index, sel):
        ntt = ''
        next_page_base_url = 'http://www.lastcall.com/category.service'
        url = sel.response.url
        idx1 = url.find('Ntt=')
        if(idx1 != -1):
            idx2 = url.find('&', idx1)
            ntt = url[idx1 + len('Ntt='):idx2]
        to_encode1 = ('{"GenericSearchReq":{"pageOffset":')
        to_encode2 = (',"pageSize":"30",'
            '"refinements":"","sort":"","endecaDrivenSiloRefinements":"0",'
            '"definitionPath":"/nm/commerce/pagedef/etemplate/Search",'
            '"advancedFilterReqItems":{"StoreLocationFilterReq":'
            '[{"locationInput":"","radiusInput":"100","allStoresInput":"false",'
            '"onlineOnly":"instore"}]},"categoryId":"","ntt":"')
        to_encode3 = \
            '","sortByFavorites":false,"isFeaturedSort":false,"prevSort":""}}'
        to_encode = to_encode1 + str(index) + to_encode2 + ntt + to_encode3
        data_encoded = base64.b64encode(to_encode)
        now = time.time()
        params_next_page_url = ''.join([next_page_base_url,
            '?data=$b64$', data_encoded,
             '&service=getFilteredEndecaResult&timestamp=', str(now)])

        return params_next_page_url

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
