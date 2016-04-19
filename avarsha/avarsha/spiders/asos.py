# -*- coding: utf-8 -*-
# @author: fsp

import scrapy.cmdline
from scrapy.http import Request
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'asos'

class AsosSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["asos.com"]
    cid = ''
    strValues = 'undefined'  # default value
    if_finished = 0
    total_items = 0
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(AsosSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def make_requests_from_url(self, url):
        # get next pages
        # get key values: cid  strValues
        cid_start_index = url.find('cid=')
        cid_end_index1 = url.find('&', cid_start_index)
        cid_end_index2 = url.find('#', cid_start_index)
        min_index = min(cid_end_index1, cid_end_index2)
        max_index = max(cid_end_index1, cid_end_index2)
        if min_index == -1:
            if max_index == -1:
                self.cid = url[cid_start_index + len('cid='):]
            else:
                self.cid = url[cid_start_index + len('cid='):max_index]
        else:
            self.cid = url[cid_start_index + len('cid='):min_index]

        if url.find('#') != -1:
            strValues_start_index = url.find('state=')
            if strValues_start_index != -1:
                strValues_end_index = url.find('&', strValues_start_index)
                if strValues_end_index != -1:
                    strValues = url[strValues_start_index + len('state='):\
                        strValues_end_index]
                else:
                    strValues = url[strValues_start_index + len('state='):]
                self.__class__.strValues = strValues.replace('%3D', '=').replace('%2C', ',').replace('%40', '@')

                item_page_url = 'http://us.asos.com/services/srvWebCategory.asmx/GetWebCategories'

                # generate post_data
                headers = {'User-Agent':self.user_agent,
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'X-Requested-With':'XMLHttpRequest',
                    'Origin': 'http://us.asos.com',
                    'Referer': url,
                    'Host': 'us.asos.com',
                    'Proxy-Connection': 'keep-alive',
                    'cookie':'asos=currencyid=2&topcatid=1000; gnv2=1; AsosCustomerAlert=; AMCV_C0137F6A52DEAFCC0A490D4C%40AdobeOrg=1766948455%7CMCMID%7C91234394806011953346826828492570991023%7CMCAID%7CNONE%7CMCAAMLH-1432523546%7C9%7CMCAAMB-1432523546%7Chmk_Lq6TPIBMW925SPhw3Q; asosbasket=basketitemcount=0&basketitemtotalretailprice=0; __utmt=1; uk-website#lang=en-US; _s_fpv=true; s_cc=true; s_pers=%20s_vnum%3D1433088000790%2526vn%253D3%7C1433088000790%3B%20s_nr%3D1431933104296-Repeat%7C1463469104296%3B%20s_invisit%3Dtrue%7C1431934904297%3B%20gpv_p10%3Ddesktop%2520us%257Ccategory%2520page%257Cwomen%2520-%2520tall%7C1431934904299%3B; _s_pl=6142; AsosExecutionEngine=ExemptionTimeout=05/18/2015 07:31; stop_mobi=yes; mbox=PC#1431918744969-546752.28_22#1433142708|session#1431931594870-282419#1431934968|check#true#1431933168; stop_mobi=yes; __utma=94689048.102923680.1431918747.1431927063.1431931597.3; __utmb=94689048.5.10.1431931597; __utmc=94689048; __utmz=94689048.1431918747.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); s_sess=%20s_ppvl%3Ddesktop%252520us%25257Ccategory%252520page%25257Cwomen%252520-%252520tall%252C15%252C15%252C878%252C1920%252C678%252C1920%252C1080%252C1%252CP%3B%20s_ppv%3Ddesktop%252520us%25257Ccategory%252520page%25257Cwomen%252520-%252520tall%252C17%252C15%252C978%252C1920%252C978%252C1920%252C1080%252C1%252CP%3B; asosStore=PreferredFloor=1000'}

                post_data_prefix = "{'cid':'" + self.cid
                post_data_prefix += '''', 'strQuery':"", 'strValues':''' + "'" + self.strValues
                post_data_prefix += '''', 'currentPage':'''
                post_data_tail = (''', 'pageSize':'36','pageSort':'-1','countryId':'2','''
                    ''''maxResultCount':''}''')

                post_data = post_data_prefix + "'" + "0" + "'" + post_data_tail
                return Request(item_page_url, callback=self.parse, method='POST', headers=headers, body=post_data, dont_filter=True)
        return Request(url, dont_filter=True)

    def _find_items_from_list_page(self, sel, item_urls):
        requests = []
        last_index = 0
        item_url_start_index = sel.response.body.find('NavigateURL":"', last_index)
        while item_url_start_index != -1:
            if self.__class__.total_items == 0:
                start_index = sel.response.body.find('TotalItems":"') + len('TotalItems":"')
                end_index = sel.response.body.find('"', start_index)
                self.__class__.total_items = int(sel.response.body[start_index:end_index])
            item_url_end_index = sel.response.body.find('"', item_url_start_index\
                + len('NavigateURL":"'))
            item_url = sel.response.body[item_url_start_index + len('NavigateURL":"'):\
                item_url_end_index]
            item_urls.append(item_url)
            requests.append(scrapy.Request(item_url, callback=self.parse_item))
            last_index = item_url_end_index
            item_url_start_index = sel.response.body.find('NavigateURL":"', last_index)
        return requests

    def find_items_from_list_page(self, sel, item_urls):
        if self.__class__.strValues == 'undefined':
            items_xpath = '//div[@class="categoryImageDiv"]/a/@href'
            item_nodes = sel.xpath(items_xpath).extract()
            requests = []
            for path in item_nodes:
                item_url = path
                item_urls.append(item_url)
                requests.append(scrapy.Request(item_url, callback=self.parse_item))
            return requests
        else:
            return self._find_items_from_list_page(sel, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """parse items in category page"""
        base_url = ''
        items_xpath = '//div[@id="paging-wrapper-btm"]//a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, items_xpath, list_urls)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []

        if self.__class__.if_finished == 0:
            if self.__class__.strValues != 'undefined':
                item_url = ('http://us.asos.com/services/srvWebCategory.asmx/'
                    'GetWebCategories')
                headers = {'User-Agent':self.user_agent,
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'X-Requested-With':'XMLHttpRequest',
                    'Origin': 'http://us.asos.com',
                    'Referer': sel.response.url,
                    'Host': 'us.asos.com',
                    'Proxy-Connection': 'keep-alive',
                    'cookie':'asos=currencyid=2&topcatid=1000; gnv2=1; AsosCustomerAlert=; AMCV_C0137F6A52DEAFCC0A490D4C%40AdobeOrg=1766948455%7CMCMID%7C91234394806011953346826828492570991023%7CMCAID%7CNONE%7CMCAAMLH-1432523546%7C9%7CMCAAMB-1432523546%7Chmk_Lq6TPIBMW925SPhw3Q; asosbasket=basketitemcount=0&basketitemtotalretailprice=0; __utmt=1; uk-website#lang=en-US; _s_fpv=true; s_cc=true; s_pers=%20s_vnum%3D1433088000790%2526vn%253D3%7C1433088000790%3B%20s_nr%3D1431933104296-Repeat%7C1463469104296%3B%20s_invisit%3Dtrue%7C1431934904297%3B%20gpv_p10%3Ddesktop%2520us%257Ccategory%2520page%257Cwomen%2520-%2520tall%7C1431934904299%3B; _s_pl=6142; AsosExecutionEngine=ExemptionTimeout=05/18/2015 07:31; stop_mobi=yes; mbox=PC#1431918744969-546752.28_22#1433142708|session#1431931594870-282419#1431934968|check#true#1431933168; stop_mobi=yes; __utma=94689048.102923680.1431918747.1431927063.1431931597.3; __utmb=94689048.5.10.1431931597; __utmc=94689048; __utmz=94689048.1431918747.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); s_sess=%20s_ppvl%3Ddesktop%252520us%25257Ccategory%252520page%25257Cwomen%252520-%252520tall%252C15%252C15%252C878%252C1920%252C678%252C1920%252C1080%252C1%252CP%3B%20s_ppv%3Ddesktop%252520us%25257Ccategory%252520page%25257Cwomen%252520-%252520tall%252C17%252C15%252C978%252C1920%252C978%252C1920%252C1080%252C1%252CP%3B; asosStore=PreferredFloor=1000'}
                post_data_prefix = "{'cid':'" + self.cid
                post_data_prefix += '''', 'strQuery':"", 'strValues':''' + \
                    "'" + self.strValues
                post_data_prefix += '''', 'currentPage':'''
                post_data_tail = (''', 'pageSize':'36','pageSort':'-1','countryId'''
                    '''':'2','maxResultCount':''}''')

                deal_item_num = 36
                cur_page = 1
                # make requests
                while deal_item_num < self.__class__.total_items:
                    post_data = post_data_prefix + "'" + str(cur_page) + "'"\
                        + post_data_tail
                    list_urls.append(item_url)
                    requests.append(scrapy.Request(item_url, callback=self.parse\
                        , method='POST', headers=headers, body=post_data))
                    cur_page += 1
                    deal_item_num += 36
                self.__class__.if_finished = 1
                return requests
        else:
            return requests

        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//span[@id="ctl00_ContentMainPage_'
            'ctlSeparateProduct_lblProductTitle"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Asos'

    def _extract_brand_name(self, sel, item):
        des_xpath = ('//div[@class="ui-tabs-panel brand-description"]'
            '//strong/text()')
        data = sel.xpath(des_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        pcode_xpath = '//span[@class="productcode"]/text()'
        data = sel.xpath(pcode_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_description(self, sel, item):
        des_xpath = '//div[@class="ui-tabs-panel product-description"]/ul'
        data = sel.xpath(des_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        images_xpath = ('//div[@class="productImagesItems items"]//img/@src')
        images = sel.xpath(images_xpath).extract()
        if len(images) != 0:
            item['image_urls'] = images

    def _extract_colors(self, sel, item):
        color_xpath = ('//div[@id="ctl00_ContentMainPage_ctlSeparateProduct'
            '_pnlColour"]//option[not(@value="-1")]/@value')
        data = sel.xpath(color_xpath).extract()
        color_list = []
        if len(data) != 0:
            for line in data:
                color_list.append(line)
            item['colors'] = color_list

    def _extract_sizes(self, sel, item):
        size_list = []
        for line in sel.response.body.split('\n'):
            idx1 = line.find('arrSzeCol_ctl00_ContentMainPage_ctlSeparateProduct[')
            if idx1 != -1:
                idx2 = line.find('True')
                if idx2 != -1:
                    idx3 = line.find('\"')
                    idx4 = line.find('\"', idx3 + 1)
                    size = line[idx3 + 1:idx4].strip()
                    if size not in size_list:
                        size_list.append(size)
        if len(size_list) != 0:
            item['sizes'] = size_list

    def _extract_price(self, sel, item):
        price_xpath = ('//*[@id="ctl00_ContentMainPage_ctlSeparateProduct'
            '_lblProductPrice"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0][len('$'):])

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
