# -*- coding: utf-8 -*-
# author: huoda

import urllib2
import json
import string

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'harpersbazaar'

class HarpersbazaarSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["harpersbazaar.com"]

    def __init__(self, *args, **kwargs):
        super(HarpersbazaarSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        base_url = 'https://shop.harpersbazaar.com/'
        if 'search' in self.start_urls[0]:
            flag = self.start_urls[0].rfind('=', 1, -1)
            tag = self.start_urls[0][flag + 1:]
            start = 0
            url1 = 'https://shop.harpersbazaar.com/search/?wt=json&start='
            url2 = '&rows=15&sort=score+desc&q=(product_name_t%3A'
            url3 = '~0.7%5E100%20OR%20description_t%3A'
            url4 = '~0.9%5E25)'
            list_url = url1 + str(start) + url2 + tag + url3 + tag + url4
            print list_url
            page = urllib2.urlopen(list_url).read()
            while len(page) > 100:
                data = json.loads(page)
                for item in data['response']['docs']:
                    item_url = item['page_name_s']
                    item_url = base_url + item_url
                    item_urls.append(item_url)
                    request = scrapy.Request(item_url, callback=self.parse_item)
                    requests.append(request)
                start += 15
                list_url = url1 + str(start) + url2 + tag + url3 + tag + url4
                print list_url
                page = urllib2.urlopen(list_url).read()


        else:
            flag = sel.response.body.find('attr_cat_id: ')
            flag_end = sel.response.body.find(' },', flag + 1)
            attr_cat_id = sel.response.body[flag + len('attr_cat_id: '):flag_end]
            print 'attr_cat_id', attr_cat_id
            start = 0
            url1 = 'https://shop.harpersbazaar.com/search/?wt=json&start='
            url2 = '&rows=15&sort=cat_product_sequence_'
            url3 = '_i+desc&q=attr_cat_id%3A'
            list_url = url1 + str(start) + url2 + attr_cat_id + url3 + attr_cat_id
            print list_url
            page = urllib2.urlopen(list_url).read()
            while len(page) > 100:
                data = json.loads(page)
                for item in data['response']['docs']:
                    item_url = item['page_name_s']
                    item_url = base_url + item_url
                    item_urls.append(item_url)
                    request = scrapy.Request(item_url, callback=self.parse_item)
                    requests.append(request)
                start += 15
                list_url = url1 + str(start) + url2 + attr_cat_id + url3 + attr_cat_id
                print list_url
                page = urllib2.urlopen(list_url).read()

        # don't need to change this line
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//head/title/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'harpersbazaar'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@class="product-entry"]//span/a[@href]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="thirdPartyId"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="description-body open"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        base_url = 'https://s3.amazonaws.com/shopbazaar-java/images/skus/'
        imgs = []
        colors = []
        flag = sel.response.body.find('var color_images')
        flag_end = sel.response.body.find('}}};', flag + 1)
        if (flag + 19) < (flag_end + 3):
            data = sel.response.body[flag + 19:flag_end + 3]
            data = json.loads(data)
            for color in data:
                colors.append(color)
                for product in data[color]:
                    if 'IMG_1050_1200' in data[color][product]:
                        img_url = base_url + data[color][product]['IMG_1050_1200']
                        imgs.append(img_url)
        if len(imgs) != 0:
            item['image_urls'] = imgs
        if len(colors) != 0:
            item['colors'] = colors

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        sizes = []
        flag = sel.response.body.find('var skus =')
        flag_end = sel.response.body.find('};', flag + 1)
        data = sel.response.body[flag:flag_end]
        flag = data.find('"name":"Size","code":"SIZE","optionValue":{"value":"')
        while flag != -1:
            flag_end = data.find('","', flag + 52)
            size = data[flag + 52:flag_end]
            sizes.append(size)
            flag = data.find('"name":"Size","code":"SIZE","optionValue":{"value":"', flag_end + 1)
        if len(sizes) != 0:
            item['sizes'] = sizes

    def _extract_price(self, sel, item):
        price_xpath = '//meta[@property="og:price:amount"]//@content'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        flag = sel.response.body.find('"listPrice":')
        flag_end = sel.response.body.find(',"', flag + 12)
        if flag != -1:
            list_price_number = sel.response.body[flag + 12:flag_end]
            if (string.atof(list_price_number)) > (string.atof(item['price'][len('USD '):])):
                item['list_price'] = self._format_price('USD', list_price_number)


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
