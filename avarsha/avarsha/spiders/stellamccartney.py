# -*- coding: utf-8 -*-
# @author: huangjunjie
import re, json, urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'stellamccartney'

class StellamccartneySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["stellamccartney.com"]

    def __init__(self, *args, **kwargs):
        super(StellamccartneySpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if idx1 != -1:
            base_url = 'http://www.stellamccartney.com/yeti/api/STELLAMCCARTNEY_US/searchIndented.json?'
            json_url = base_url + url[idx1 + 1:] + '&baseurl=http://www.stellamccartney.com/searchresult.asp'
            return json_url
        return url
    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        url = sel.response.url
        base_url = 'http://www.stellamccartney.com'
        if url.find('yeti/api') != -1:
            requests = []
            json_html = urllib2.urlopen(url).read()
            url_json = json.loads(json_html)
            for every_url in url_json['ApiResult']['Items']:
                path = every_url['SingleSelectLink']
                if path.find(base_url) == -1:
                    item_url = base_url + path
                    item_urls.append(item_url)
                    request = scrapy.Request(item_url, callback=self.parse_item)
                    requests.append(request)
            return requests
        else:

            items_xpath = '//div[@class="productInfo"]/a/@href'
            return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath1 = ('//span[@class="modelName"]/text()')
        data = sel.xpath(title_xpath1).extract()
        if len(data) != 0:
            item['title'] = data[0]


    def _extract_store_name(self, sel, item):
        item['store_name'] = 'stellamccartney'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Stella_Mccartney'

    def _extract_sku(self, sel, item):
        url = sel.response.url
        m = re.search(r'_cod(?P<sku>\w*).html', url)
        if m:
            item['sku'] = m.groupdict('sku')['sku']

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="descriptionWrapper"]/ul//li/div/p'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            desc = "".join(data)
            item['description'] = desc


    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//ul[@id="alternateList"]//li/div/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        for small_img in data:
            large_img_index = small_img.rfind('8')
            large_img = small_img[:large_img_index] + '13r' + small_img[large_img_index + 1:]
            imgs.append(large_img)
        item['image_urls'] = imgs
    def _get_json(self, sel):
        json_xpath = '//script[not(@src) and @type="text/javascript"]'
        data = sel.xpath(json_xpath).extract()
        if len(data) != 0:
            str = re.sub('[\r\n\t]', '', data[2])
            m = re.search(r'jsinit_item=(?P<item>.*?});', str)
            items = m.groupdict('item')['item']
            m = re.search(r'\"CURRENTITEM\":(?P<currentitem>.*), \"ALTERNATE\"', items)
            item_json = json.loads(m.groupdict('currentitem')['currentitem'])
            return item_json

    def _extract_colors(self, sel, item):
        item_json = self._get_json(sel)
        if item_json:
            item_color = item_json['json']['Colors'][0]['Color']
            if type(item_color) == 'list':
                item['colors'] = item_json['json']['Colors'][0]['Color']
            else:
                item_color1 = []
                item_color1.append(item_color)
                item['colors'] = item_color1

    def _extract_sizes(self, sel, item):
        item_json = self._get_json(sel)
        if item_json:
            item['sizes'] = item_json['json']['Colors'][0]['SizeW']

    def _extract_stocks(self, sel, item):
        pass


    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="newprice"]/'
            'span[@class="priceValue"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price = data[0].strip()
            item['price'] = self._format_price('USD', price)




    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="oldprice"]/'
            'span[@class="priceValue"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price = data[0].strip()
            item['list_price'] = self._format_price('USD', price)


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
