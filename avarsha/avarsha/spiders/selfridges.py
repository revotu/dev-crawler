# -*- coding: utf-8 -*-
# author fsp

import urllib2

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'selfridges'

class SelfridgesSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["selfridges.com"]
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(SelfridgesSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = ''
        items_xpath = '//div[@class="productContainer"]/a[1]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def _find_items_from_list_page(self, sel, base_url, items_xpath, item_urls):
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = base_url + path
            item_urls.append(item_url)
            requests.append(scrapy.Request(item_url, callback=self.parse_item))
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="pageNumberInner"]//a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@class="description"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Selfridges'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//input[@name="productBrand"]/@value'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        pcode_xpath = '//input[@name="productId"]/@value'
        data = sel.xpath(pcode_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip('\r').strip('\t').strip('\n').strip()

    def _extract_description(self, sel, item):
        des_xpath = '//div[@class="productDetailsInner"]/div/script//text()'
        data = sel.xpath(des_xpath).extract()
        des = data[0]
        for i in range(len(data)):
            des += data[i].strip('\n').strip('\t').strip()
        item['description'] = des.strip()

    def _extract_image_urls(self, sel, item):
        image_url_xpath = ('//img[@itemprop="image"]/@src')
        image_url = sel.xpath(image_url_xpath).extract()
        if len(image_url) != 0:
            start_index = image_url[0].rfind('/') + len('/')
            end_index = image_url[0].rfind('?') + len('?')
            image_url = image_url[0][start_index:end_index]
            key = image_url[:image_url.find('M?')]
            url_head = 'http://images.selfridges.com/is/image//selfridges?req=set,json&imageset={'
            url_middle = image_url.replace('M?', 'IMGSET') + ',' + image_url[:-1] + ',' + image_url.replace('M?', '360')
            url_tail = '}&defaultImage='
            url = url_head + url_middle + url_tail
            try:
                content = urllib2.urlopen(url).read()
            except Exception, e:
                print e
            else:
                text_list = ['M']
                start_index = content.find(key)
                while start_index != -1:
                    start_index += len(key)
                    end_index = content.find('"', start_index)
                    text = content[start_index:end_index]
                    if text not in text_list:
                        if text != 'IMGSET':
                            text_list.append(text)
                    start_index = content.find(key, end_index)
            images_head = 'http://images.selfridges.com/is/image//selfridges/'
            images_tail = '?$PDP_M_ZOOM$'
            images = []
            for line in text_list:
                images.append(images_head + key + line + images_tail)
            if len(images) != 0:
                item['image_urls'] = images

    def _extract_colors(self, sel, item):
        color_xpath = '//label[@itemprop="color"]/input[@name="Colour"]/@value'
        data = sel.xpath(color_xpath).extract()
        color_list = []
        if len(data) != 0:
            for line in data:
                color_list.append(line)
            item['colors'] = color_list

    def _extract_sizes(self, sel, item):
        size_list = []
        form_names_xpath = '//form[@name="OrderItemAddForm"]/input/@name'
        form_values_xpath = '//form[@name="OrderItemAddForm"]/input/@value'
        form_names = sel.xpath(form_names_xpath).extract()
        form_values = sel.xpath(form_values_xpath).extract()

        url_head = ('http://www.selfridges.com/webapp/wcs/stores/servlet/'
            'AjaxStockStatusView?attr=Colour&attrval=')
        url_tail = ''
        for i in range(len(form_names)):
            url_tail += '&' + form_names[i] + '=' + form_values[i].replace(' ', '+')
        url_tail += '&Colour='

        for color in item['colors']:
            url = url_head + color + url_tail + color
            url2 = url_head + color + url_tail + color + '&Size=SELECT+SIZE'
            url = url.replace(' ', '%20')
            url2 = url2.replace(' ', '%20')
            req = urllib2.Request(url)
            req2 = urllib2.Request(url2)
            try:
                content = urllib2.urlopen(req).read()
                content2 = urllib2.urlopen(req2).read()
            except Exception, e:
                print e
            else:
                size_start_index = content.find('name":"Size","value":"')
                if size_start_index != -1:
                    while size_start_index != -1:
                        size_start_index += len('name":"Size","value":"')
                        size_end_index = content.find('"', size_start_index)
                        size = content[size_start_index:size_end_index]
                        size_start_index = content.find('name":"Size","value":"', size_end_index)
                        test_content = content[size_end_index:size_start_index]
                        if test_content.find('false') == -1:
                            size_list.append(size)
                else:
                    size_start_index = content2.find('name":"Size","value":"')
                    while size_start_index != -1:
                        size_start_index += len('name":"Size","value":"')
                        size_end_index = content2.find('"', size_start_index)
                        size = content2[size_start_index:size_end_index]
                        size_start_index = content2.find('name":"Size","value":"', size_end_index)
                        test_content = content2[size_end_index:size_start_index]
                        if test_content.find('false') == -1:
                            size_list.append(size)
        if len(size_list) != 0:
            item['sizes'] = size_list

    def _extract_list_price(self, sel, item):
        price_xpath = '//p[@class="wasPrice"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price = data[0].strip().replace(u'£', '')
            item['list_price'] = self._format_price('GBP', price)

    def _extract_price(self, sel, item):
        price_xpath = '//p[@class="price"]/text()'
        data = sel.xpath(price_xpath).extract()
#         print data[0]
        if len(data) != 0:
            price = data[0].strip().replace(u'£', '')
            item['price'] = self._format_price('GBP', price)

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
