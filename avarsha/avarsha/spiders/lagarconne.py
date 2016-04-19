# -*- coding: utf-8 -*-
# author: huoda

import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'lagarconne'

class LagarconneSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["lagarconne.com"]

    def __init__(self, *args, **kwargs):
        super(LagarconneSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        data = sel.response.url
        if data.find('category') != -1:
            flag = data.find('/', \
                len('http://www.lagarconne.com/store/category/') + 1)
            flag_end = data.find('/', flag + 1)
            sid = data[flag + 1:flag_end]
            base_url = data[0:flag + 1].replace('category', 'item')
            source_url1 = 'http://www.lagarconne.com/store/load_products.htm?offset='
            source_url2 = '&sid=' + sid
            offset = 0
            source_url = source_url1 + str(offset) + source_url2
            resources = urllib2.urlopen(source_url).read()
            while (resources != '\xef\xbb\xbf0'):
                flag = resources.find('seo_code')
                while(flag != -1):
                    flag_end = resources.find('","', flag + 10)
                    temp = resources[flag + 11:flag_end]
                    temp = temp.replace('\/', '/')
                    item_url = base_url + temp
                    item_urls.append(item_url)
                    requests.append(scrapy.Request(item_url, \
                        callback=self.parse_item))
                    flag = resources.find('seo_code', flag_end + 1)
                offset += 1
                source_url = source_url1 + str(offset) + source_url2
                resources = urllib2.urlopen(source_url).read()
            return requests
        else:
            flag = data.find('search.htm?s=')
            tab = data[flag + 13:]
            offset = 0
            base_url = 'http://www.lagarconne.com/store/item/0/'
            url1 = 'http://www.lagarconne.com/store/search_item.htm?offset='
            url2 = '&keyword='
            source_url = url1 + str(offset) + url2 + tab
            resources = urllib2.urlopen(source_url).read()
            print resources
            while (resources != '\xef\xbb\xbf0'):
                flag = resources.find('seo_code')
                while(flag != -1):
                    flag_end = resources.find('","', flag + 10)
                    temp = resources[flag + 11:flag_end]
                    temp = temp.replace('\/', '/')
                    item_url = base_url + temp
                    item_urls.append(item_url)
                    requests.append(scrapy.Request(item_url, \
                        callback=self.parse_item))
                    flag = resources.find('seo_code', flag_end + 1)
                offset += 1
                source_url = url1 + str(offset) + url2 + tab
                resources = urllib2.urlopen(source_url).read()
            return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        flag = sel.response.url.rfind('/')
        data = sel.response.url[flag + 1:]
        data = data.replace('-', ' ')
        item['title'] = data

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'lagarconne'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//div[@class="product_share"]/../h2/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@class="product_sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][2:]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="accordion-1"]/p'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//div[@class="images-wp"]//@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        colors_xpath = '//label[@class="checked"]/../label//text()'
        data = sel.xpath(colors_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        sizes_all = '//div[@id="select-size"]//label//text()'
        size_all = sel.xpath(sizes_all).extract()
        x = []
        for i in size_all:
            i = i.strip()
            if len(i) != 0:
                x.append(i)
        sizes_empty = '//div[@id="select-size"]//label/*[@disabled]/..//text()'
        size_empty = sel.xpath(sizes_empty).extract()
        for i in size_empty:
            i = i.strip()
            if len(i) != 0:
                x.remove(i)
        if len(x) != 0:
            item['sizes'] = x

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="price-wp"]/div/p/font/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            flag = data[0].find('$')
            data = data[0][flag + 1:]
            item['price'] = self._format_price('USD', data)
            list_price_xpath = ('//div[@class="price-wp"]/div/p/s/text()')
            data = sel.xpath(list_price_xpath).extract()
            if len(data) != 0:
                flag = data[0].find('$')
                data = data[0][flag + 1:]
                item['list_price'] = self._format_price('USD', data)
        else:
            price_xpath = ('//div[@class="price-wp"]//p[@class="price" '
                'and @itemprop="price"]//text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                flag = data[0].find('$')
                data = data[0][flag + 1:]
                item['price'] = self._format_price('USD', data)

    def _extract_list_price(self, sel, item):
        pass

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        item['is_free_shipping'] = True

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
