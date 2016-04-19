# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'net-a-porter'

class Net_a_porterSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["net-a-porter.com"]

    def __init__(self, *args, **kwargs):
        super(Net_a_porterSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.net-a-porter.com'
        items_xpath = ('//*[@class="product-image"]/a/@href | '
            '//*[@class="product-image   "]/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        nexts_xpath = '//*[@class="pagination-links"]/a/@href'
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find('..') != -1:
                base_url = 'http://www.net-a-porter.com/us/en/d/Shop'
                if path.find(base_url) == -1:
                    list_url = base_url + path[len('..'):]
                list_url = list_url.replace('&__proto__=[object Object]', '')
            elif path.find('Search') != -1:
                base_url = 'http://www.net-a-porter.com'
                if path.find(base_url) == -1:
                    list_url = base_url + path
                list_url = list_url.replace(' ', '%20')
            list_urls.append(list_url)
            requests.append(scrapy.Request(list_url, callback=self.parse))
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'net-a-porter'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@itemprop="brand"]/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        index = sel.response.url.rfind('/')
        data = sel.response.url[index + 1:]
        if len(data) != 0:
            item['sku'] = data.strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desc_xpath = '//*[@class="tabBody1 tabContent"]'
        data = sel.xpath(desc_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        images_xpath = '//*[@property="og:image"]/@content'
        data = sel.xpath(images_xpath).extract()
        img_list = []
        if len(data) != 0:
            for img in data:
                img_list.append(img.replace('pp', 'xl'))
            item['image_urls'] = img_list

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//*[@itemprop="price"]/text() | '
            '//*[@class="now"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            idx = data[0].strip().find('$')
            price_number = data[0].strip()[idx + 1:]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@class="was"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0 :
            idx = data[0].strip().find('$')
            list_price_number = data[0].strip()[idx + 1:]
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