# -*- coding: utf-8 -*-
# @author: donglongtu

import gzip
import json
import re
import urllib
import urllib2
from StringIO import StringIO

import scrapy.cmdline
from scrapy import log

from avarsha_spider import AvarshaSpider
from avarsha.items import ProductItem

_spider_name = 'wish'

class WishSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["wish.com"]
    headers = {
        'Accept': '*/*',
        'Accept-Language':'en-US;q=1',
        'User-Agent': 'Wish/138 (iPhone; iOS 8.3; Scale/3.00)',
        'Cookie': '_xsrf=1; _appLocale=zh-Hans; sweeper_session="OTJjMGEyZ'
        'TgtNWU3YS00MjM3LTllNjctM2YwNjQxODZlZjZlMjAxNS0wNC0yMyAwNzoxNDo1NC4'
        '5MTcxMTU=|1429773294|f1e150cbcd231da2fdbf63ee79d25dad7b9354de"; '
        'bsid=ff3d3ab5ca4c4e9bbf3eeae17e395bc8',
        'Accept-Encoding': 'gzip'
           }

    def __init__(self, *args, **kwargs):
        super(WishSpider, self).__init__(*args, **kwargs)

    def fetch_wish_data(self, url, data, headers):
        req = urllib2.Request(url, urllib.urlencode(data), headers)

        r = urllib2.urlopen(req)
        if r.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(r.read())
            f = gzip.GzipFile(fileobj=buf)
            return json.loads(f.read())
        else:
            return json.loads(r.read())

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        get_filtered_feed_params = {
            '_app_type': 'wish',
            '_capabilities[]': '1',
            '_capabilities[]': '2',
            '_capabilities[]': '4',
            '_capabilities[]': '6',
            '_capabilities[]': '7',
            '_capabilities[]': '8',
            '_client': 'iosapp',
            '_version': '3.10.0',
            '_xsrf': '1',
            'app_device_id': 'a4dbc15c30e97dc20c42eaddc2f77271fcb9e226',

            # change the following #
            'count': '30',
            'offset': '0',
            'request_id': 'tag_53dc186321a86318bdc87ef8'
        }

        get_filtered_feed_url = 'http://www.wish.com/api/feed/get-filtered-feed'

        i = 0
        while True:
            get_filtered_feed_params['offset'] = i * 30
            jdata = (self.fetch_wish_data(get_filtered_feed_url,
                 get_filtered_feed_params, self.headers))
            if jdata['data'].has_key('products') == False:
                break
            jdata_data_products = jdata['data']['products']
            item_numbers = len(jdata_data_products)
            requests = []
            for j in range(item_numbers):
                item_id = jdata_data_products[j]['id']
                if item_id != '':
                    item_url = 'https://www.wish.com/m/c/' + item_id
                    item_urls.append(item_url)
                    requests.append((scrapy.Request(item_url,
                        callback=self.parse_item)))
            for request in requests:
                yield request
            i += 1

    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def parse_item(self, response):
        self.log('Parse item link:  %s' % response.url, log.DEBUG)

        item = ProductItem()

        item['url'] = response.url

        index = response.url.rfind('/')
        data = response.url[index + 1:]
        if len(data) != 0:
            item_id = data

        get_product_params = {
            '_app_type': 'wish',
            '_capabilities[]': '1',
            '_capabilities[]': '2',
            '_capabilities[]': '4',
            '_capabilities[]': '6',
            '_capabilities[]': '7',
            '_capabilities[]': '8',
            '_client': 'iosapp',
            '_version': '3.10.0',
            '_xsrf': '1',
            'app_device_id': 'a4dbc15c30e97dc20c42eaddc2f77271fcb9e226',

            # change the following #
            'cid':item_id,
            'comment_preview_length':'2',
            'related_contest_count':'9',
        }
        get_product_url = 'http://www.wish.com/api/product/get'
        jdata_product = self.fetch_wish_data(get_product_url,
             get_product_params, self.headers)
        jdata_product_contest = jdata_product['data']['contest']
        jdata_product_info = (jdata_product['data']['contest']
            ['commerce_product_info'])
        jdata_var = jdata_product_info['variations']

        item['store_name'] = 'Wish'

        if jdata_product_contest.has_key('name') == True:
            item['title'] = jdata_product_contest['name']

        if jdata_product_info['variations'][0].has_key('merchant_name') == True:
            item['brand_name'] = (jdata_product_info['variations']
                [0]['merchant_name'])

        if item_id != '':
            item['sku'] = item_id

        if jdata_product_contest.has_key('description') == True:
            item['description'] = jdata_product_contest['description']

        if jdata_product_info.has_key('sizing_chart_url') == True:
            size_chart_url = jdata_product_info['sizing_chart_url']
            try:
                content = urllib2.urlopen(size_chart_url).read()
                content = self._remove_escape(content)
                size_chart_reg = re.compile(r'(\"charts\".+?),\"use_inches\"')
                data = size_chart_reg.findall(content)
                if len(data) != 0:
                    item['size_chart'] = data[0]
            except:
                pass

        imgs_list = []
        if jdata_product_contest.has_key('extra_photo_urls') == True:
            pics_dict = jdata_product_contest['extra_photo_urls']
            for key in pics_dict:
                imgs_list.append(pics_dict[key].replace('small', 'large'))
        imgs_list.append('https://contestimg.wish.com/api/image/fetch?contest_'
                         'id=' + item['sku'] + '&w=809&h=809')
        item['image_urls'] = imgs_list

        if jdata_var[0].has_key('localized_price') == True:
            jdata_price = jdata_var[0]['localized_price']
            price_number = str(jdata_price['localized_value'])
            if jdata_price['currency_code'] == 'USD' :
                item['price'] = self._format_price('USD', price_number)
            elif jdata_price['currency_code'] == 'CNY':
                item['price'] = self._format_price('CNY', price_number)

        if jdata_var[0].has_key('localized_retail_price') == True:
            jdata_list_price = jdata_var[0]['localized_retail_price']
            list_price_number = str(jdata_list_price['localized_value'])
            if jdata_list_price['currency_code'] == 'USD' :
                list_price = self._format_price('USD', list_price_number)
            elif jdata_list_price['currency_code'] == 'CNY':
                list_price = self._format_price('USD', list_price_number)
            if list_price != item['price']:
                item['list_price'] = list_price

        return item

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
