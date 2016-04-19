# -*- coding: utf-8 -*-
# author: tanyafeng

import re
import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'yoox'

class YooxSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["yoox.com"]

    def __init__(self, *args, **kwargs):
        super(YooxSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.yoox.com'
        items_xpath = '//*[@class="itemlink"]/@href'

        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = self.convert_url(path)
            if path.find(base_url) == -1:
                item_url = base_url + self.convert_url(path)
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback = self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//*[@rel="next"]/@href'

        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_urls.append(self.convert_url(list_url))
            request = scrapy.Request(list_url, callback = self.parse)
            requests.append(request)
        return requests

    def convert_url(self, url):
        url_str = url.split('#')
        return url_str[0].replace(' ' , '%20')

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="issw"]/@data-issw-name'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Yoox'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@itemprop="brand"]/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@id="itemInfoCod10"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="dataContent selected"]/ul'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        img_xpath = '//*[@class="colorsizelist"]/li/img/@src'
        swatch_xpath = '//*[@id="itemThumbs"]/li/img/@src'
        swatch_pattern = re.compile('_\d*_(.*jpg)')
        replace_pattern = re.compile('_.*_.*jpg')
        data = sel.xpath(img_xpath).extract()
        swatch_list = []
        swatch_data = sel.xpath(swatch_xpath).extract()
        if len(swatch_data) != 0:
            for swatch_url in swatch_data:
                match = swatch_pattern.findall(swatch_url)
                if len(match) != 0:
                    swatch_list.append(match[0])
            if len(data) != 0:
                for swatch_str in swatch_list:
                    for img_str in data:
                        imgs.append(replace_pattern.sub('_14_' + swatch_str, \
                            img_str))
            else:
                for swatch_str in swatch_data:
                    imgs.append(re.sub('_\d*_' , '_14_' , swatch_str))
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        colors = []
        color_pattern = re.compile('"ColorId":\\d*,"Name":"(.*?)"')
        for line in sel.response.body.split('\n'):
            if line.find('colorSizeJson') != -1:
                match = color_pattern.findall(line)
                if len(match) != 0:
                    for color_str in match:
                        if color_str.find('(-)') == -1:
                            colors.append(color_str)
                break
        if len(colors) != 0:
            item['colors'] = colors

    def _extract_sizes(self, sel, item):
        sizes = []
        size_pattern = re.compile('"Id":\\d*,"Name":"(.*?)"')
        for line in sel.response.body.split('\n'):
            if line.find('colorSizeJson') != -1:
                match = size_pattern.findall(line)
                if len(match) != 0:
                    for size_str in match:
                        if size_str.find('--') == -1:
                            sizes.append(size_str)
                break
        if len(sizes) != 0:
            item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@itemprop="price"]/text()'
        currency_xpath = '//*[@class="priceCurrency"]/@content'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_strs = data[0].strip().split(' ')
            price_number = ''.join(price_strs[len(price_strs) - 1].split(','))
            currency_data = sel.xpath(currency_xpath).extract()
            if len(currency_data) != 0:
                item['price'] = self._format_price(currency_data[0], \
                    price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@class="oldprice"]/text()'
        currency_xpath = '//*[@class="priceCurrency"]/@content'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_strs = data[0].strip().split(' ')
            price_number = ''.join(price_strs[len(price_strs) - 1].split(','))
            currency_data = sel.xpath(currency_xpath).extract()
            if len(currency_data) != 0:
                item['list_price'] = self._format_price(currency_data[0], \
                    price_number)

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
    scrapy.cmdline.execute(
        argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
