# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline

import re

import urllib2

import json

from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'outletbicocca'

class A6pmSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["outletbicocca.com"]

    def __init__(self, *args, **kwargs):
        self.header = {'Cookie' : 'eu_cookie_notice=1; PHPSESSID=9540l19pknstph75ahhag4nbi3; __insp_wid=589448434; __insp_nv=true; __insp_ref=aHR0cDovL291dGxldGJpY29jY2EuY29tLzM0LWFjY2Vzc29yaQ%3D%3D; __insp_norec_sess=true; __insp_slim=1435389342039; 4b5e8c9eaece5f8a80b1269a9e41a884=TjXpxQAMIs0%3DE4CmIe33WgE%3DPgqrkafIvZc%3DajwZ%2B9s02zs%3Dk4Luq%2BNuU%2Bc%3DG%2Bj1Xxm9plQ%3D7ukBNAndPKM%3D41ZUOhgdw%2BQ%3DiPvmss0yksE%3Dptu8AlqMAIk%3DWRlWeL%2BuBE0%3DVM1iJAvjWXU%3DWHNXJLasOsM%3DZQB7X95B5kU%3DEqKBJgEUuLw%3DBm4IRLskubA%3Djys3sZVEysI%3DIDE3SPi83X0%3D1jrwvYPJFH4%3DeEaHS7%2FS3ww%3DXAFDr88gINI%3DhoV633esBmo%3DUD0EIdIqCmo%3DboSeaHcKwh4%3DhoV633esBmo%3DB0ZPxM7wO0Y%3DUzKHZj70Q64%3DOdLGEMDX0pI%3DWpbo6FIPel0%3DC6AuBJMcmCY%3D3XXpnwfDsGw%3DZAzXY54wA8U%3D4l9qmObeBMk%3Dyvh62qCX5Go%3DsQt%2FcYYz2EE%3Dtx2gV5Z1jok%3Di3gLjQaX8b8%3DCPnp9edJqV4%3D; __utma=60464435.224458378.1434337310.1435382725.1435385779.6; __utmb=60464435.15.10.1435385779; __utmc=60464435; __utmz=60464435.1434337310.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'}
        super(A6pmSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        if url.find('search.php?') != -1:
            return url
        self.ident = re.search(re.compile('\d+'), url).group()
        self.dic = {}
        self.paras = re.findall(re.compile('[a-z]+\:\d+'), url)
        idx = url.find('#')
        if idx != -1:
            return url[:idx]
        return url

    def find_items_from_list_page(self, sel, item_urls):
        if sel.response.url.find('search.php?') != -1:
            base_url = ''
            items_xpath = '//*[@id="product_list"]//li/a[1]/@href'
            return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

        idx = 0
        last_url = ''
        while idx < len(self.paras):
            last_url += '&' + self.paras[idx].replace(':', '_' + str(idx) + '=')
            idx += 1
        page = 1
        requests = []
        while True:
            pre_url = ('http://outletbicocca.com/modules/coremanager/modules/'
            'filtersearch/filtersearch.json.php?flag=category&init_filter=0'
            '&act=filter&ident=%s&isRange=0&page=%d&perpage=21&'
            'orderby=position&orderway=asc' % (self.ident, page))
            cate_url = pre_url + last_url
            request = urllib2.Request(cate_url)
            response = urllib2.urlopen(request)
            data = json.loads(response.read())
            sel = Selector(text=self._remove_escape(data['products']))
            for item_url in sel.xpath('//li/a[1]/@href').extract():
                item_urls.append(item_url)
                requests.append(scrapy.Request(item_url,
                    callback=self.parse_item))
            if page * 21 >= int(data['filterCount']):
                break
            page += 1
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        if sel.response.url.find('search.php?') != -1:
            base_url = 'http://outletbicocca.com/'
            nexts_xpath = '//*[@id="pagination"]/ul//li/a/@href'
            return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="pb-left-column"]/h2/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Outletbicocca'

    def _extract_brand_name(self, sel, item):
        for line in sel.response.body.split('\n'):
            idx1 = line.find('brand: \"')
            if idx1 != -1:
                idx2 = line.find('\",', idx1)
                item['brand_name'] = line[idx1 + len('brand: \"'):idx2]
                break

    def _extract_sku(self, sel, item):
        sku_xpath = '//input[@name="id_product"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="sheets align_justify"]/div/ul/*'
        data = sel.xpath(description_xpath).extract()
        content = ''
        if len(data) != 0:
            for line in data:
                content += line.strip()
        item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//*[@id="thumbs_list"]/ul//li/a/@href'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            imgs = []
            for line in data:
                imgs.append('http://outletbicocca.com/' + line)
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_list_xpath = '//*[@id="attributes"]/p[2]/select//option/@title'
        data = sel.xpath(color_list_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//*[@id="attributes"]/p[1]/select//option/@title'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        request = urllib2.Request(sel.response.url, headers=self.header)
        sel = Selector(text=urllib2.urlopen(request).read())
        price_xpath = '//span[@id="our_price_display"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

        list_price_xpath = '//span[@id="old_price_display"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0][len('$'):].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

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
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
