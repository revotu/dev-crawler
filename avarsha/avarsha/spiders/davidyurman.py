# -*- coding: utf-8 -*-
# author: tanyafeng

import urllib2

import scrapy.cmdline
from scrapy import log
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'davidyurman'

class DavidyurmanSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["davidyurman.com"]
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(DavidyurmanSpider, self).__init__(*args, **kwargs)

        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.davidyurman.com'
        items_xpath = '//*[@class="plp-item__link"]/@href'

        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + self.convert_url(path)
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback = self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.davidyurman.com'
        nexts_xpath = '//*[@class="next is-active"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def convert_url(self, url):
        return url.replace(' ', '%20')

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@property="og:title"]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Davidyurman'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Davidyurman'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="product-social-share-parent"]/@data-sku'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="pd-details"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ' '.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        base_url = 'http://www.davidyurman.com'
        img_xpath = '//*[@class="pd-images-primary"]/div/div/div/img/@src'
        colors_image_xpath = ('//*[@class="pd-colors-selector pd-swatch"]'
            '/div/a/@data-partial')
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            for img_url in data:
                imgs.append('http:' + img_url)
        data = sel.xpath(colors_image_xpath).extract()
        if len(data) != 0:
            for fetch_img_url in data:
                request = urllib2.Request(base_url + fetch_img_url, \
                    headers = sel.response.request.headers)
                try:
                    img_response = urllib2.urlopen(request)
                    img_sel = Selector(text = \
                        img_response.read().decode("UTF-8"))
                    img_data = img_sel.xpath(img_xpath).extract()
                    if len(img_data) != 0:
                        for img_url in img_data:
                            imgs.append('http:' + img_url)
                except urllib2.URLError, e:
                    self.log('Exception in extract_image_urls: %s' % e.code, \
                        log.ERROR)

        item['image_urls'] = imgs


    def _extract_colors(self, sel, item):
        color_xpath = ('//*[@class="pd-colors-selector pd-swatch"]'
            '/div/a/@data-name')
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        sizes = []
        size_xpath = '//*[@name="size"]/option[@data-addmethod]/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            for size_str in data:
                tmp_size = size_str.split('-')
                sizes.append(tmp_size[0].strip())
            item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_str = []
        currency_xpath = '//*[@property="product:price:currency"]/@content'
        price_xpath = '//*[@property="product:price:amount"]/@content'
        data = sel.xpath(currency_xpath).extract()
        if len(data) != 0:
            price_str.append(data[0])
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_str.append(data[0])
        if len(price_str) == 2:
            item['price'] = self._format_price(price_str[0], price_str[1])

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
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
