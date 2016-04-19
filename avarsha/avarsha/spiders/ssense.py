# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re
import urllib

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'ssense'

class SsenseSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["ssense.com"]

    def __init__(self, *args, **kwargs):
        super(SsenseSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.ssense.com'
        items_xpath = '//div[@class="browsing-product-item"]/a/@href'
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            path = urllib.quote(path.encode('utf-8'))
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'https://www.ssense.com'
        nexts_xpath = '//div[@class="span16 text-center"]//ul[1]//li/a/@href'
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            idx = list_url.find('?q=')
            if(idx != -1):
                parmt = list_url[idx + len('?q='):]
                parmt = (parmt
                    .replace('&', '%26').replace(' ', '%20')
                    .replace('/', '%2F').replace('[]', '%5B%5D'))
                list_url = list_url[:idx + len('?q=')] + parmt
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//strong[@class="product-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'SSENSE'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'SSENSE'

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@itemprop="sku"]/@content'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = str(data[0].strip())

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//p[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        _description = ''
        if len(data) != 0:
            _description = ''.join([_description, data[0]])
        item['description'] = _description.strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_url_xpath = ('//div[@class='
            '"product-images-zoom-image-wrapper"]/img/@data-src')
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        if(len(data_imgs) != 0):
            item['image_urls'] = data_imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@itemprop="offers"]//span[@class="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if(len(data) != 0):
            data_re = re.compile(r'USD|[ $]')
            item['price'] = self._format_price(
                'USD', data_re.sub('', data[0]).strip())

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@itemprop="offers"]'
            '//span[@class="price sale"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if(len(data) != 0):
            data_re = re.compile(r'USD|[ $]')
            item['list_price'] = self._format_price(
                'USD', data_re.sub('', data[0]).strip())

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        is_free_shipping_xpath = ('//p[@class='
            '"sale-free-ship-banner sale-free-ship-united-states"]/text()')
        is_free_shipping = sel.xpath(is_free_shipping_xpath).extract()
        if(len(is_free_shipping) != 0):
            line = is_free_shipping[0]
            idx = line.find('Free shipping')
            if(idx != -1):
                item['is_free_shipping'] = True

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
