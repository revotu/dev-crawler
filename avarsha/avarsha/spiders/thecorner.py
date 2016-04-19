# -*- coding: utf-8 -*-
# @author: donglongtu

import re
import urllib2

import scrapy.cmdline
from scrapy.http import Request
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'thecorner'

class ThecornerSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["thecorner.com"]
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36')
    cookies = {}

    def __init__(self, *args, **kwargs):
        super(ThecornerSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def set_crawler(self, crawler):
        super(ThecornerSpider, self).set_crawler(crawler)
        crawler.settings.set('COOKIES_ENABLED', True)

    def make_requests_from_url(self, url):
        if url.find('RenderProducts') != -1:
            url_site = 'http://www.thecorner.com/us/women'
            req = urllib2.Request(url_site, headers={'User-Agent':
                self.user_agent})
            response = urllib2.urlopen(req)
            cookie = response.headers.get('Set-Cookie')
            session_reg = re.compile('ytos-session-THECORNER=(.+?);')
            data = session_reg.findall(cookie)
            self.cookies = {'ytos-session-THECORNER':data[0] }
            return Request(url, cookies=self.cookies, dont_filter=True)
        return Request(url, dont_filter=True)

    def convert_url(self, url):
        idx = url.find('#')
        parameters = ''
        if idx != -1:
            data = eval(url[idx + 1:])
            for key in data:
                if type(data[key]) == int:
                    parameters += key + '=' + str(data[key]) + '&'
                elif type(data[key]) == str:
                    parameters += key + '=' + data[key] + '&'
                else:
                    values = ''
                    if len(data[key]) > 1:
                        for i in range(len(data[key]) - 1):
                            values += data[key][i] + '%2C'
                        values += data[key][len(data[key]) - 1]
                    elif len(data[key]) == 1:
                        values += data[key][0]
                    parameters += key + '=' + values + '&'
            url = ('http://www.thecorner.com/Search/RenderProducts?%ssiteCode'
                '=THECORNER_US' % parameters)
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//*[@class="itemContentWrapper"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.thecorner.com'
        nexts_xpath = '//*[@class="nextPage"]/a/@href'
        if sel.response.url.find('RenderProducts') == -1:
            nexts = sel.xpath(nexts_xpath).extract()
            requests = []
            for path in nexts:
                list_url = path
                if path.find(base_url) == -1:
                    list_url = base_url + path
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
            return requests
        else:
            requests = []
            start_url = sel.response.url
            idx_1 = start_url.find('?')
            idx_2 = start_url.find('siteCode')
            pages_parameters = start_url[idx_1 + 1:idx_2 - 1]
            pages = (pages_parameters.replace('=', '%3D').replace('&', '%26')
                .replace('%2C', '%252C'))
            pages_url = ('http://www.thecorner.com/yTos/Plugins/SearchPlugin/'
                'RenderTotalResults/THECORNER_US/D/?apiRequest=%s&showLabel'
                '=true' % pages)
            req = urllib2.Request(pages_url, headers={'User-Agent':
                self.user_agent})
            response = urllib2.urlopen(req).read()
            totals_reg = re.compile(r'<span class=\'totalResultsCount\''
                '>(.+?)</span>')
            totals = totals_reg.findall(response)
            flag = int(totals[0]) % 30
            if flag == 0:
                max_page = int(totals[0]) / 30
            else:
                max_page = int(totals[0]) / 30 + 1
            i = 2
            while i <= max_page:
                try:
                    list_url = start_url.replace('page=1', ('page=%s' % i))
                    list_urls.append(list_url)
                    request = scrapy.Request(list_url, cookies=self.cookies,
                        callback=self.parse)
                    requests.append(request)
                    i += 1
                except:
                    break
            return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//title/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            index = data[0].find('-')
            item['title'] = data[0][:index].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Thecorner'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@class="brandName"]/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="productCode"]/span[@class="text"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//*[@data-ytos-tab="Details"]/div[@class="desc'
            'riptionContent"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//*[@class="alternativeImages"]/li/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for img in data:
                index1 = img.rfind('/')
                index2 = img.rfind('_')
                code = img[index1 + 1:index2]
                img_large = img[:index1 + 1] + code.upper() + img[index2:]
                imgs.append(img_large.replace('_8_', '_14_'))
        item['image_urls'] = list(set(imgs))

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@class="full price"]/span[@class="value"]/'
            'text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

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

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()