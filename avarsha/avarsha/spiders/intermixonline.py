# -*- coding: utf-8 -*-
# @author: donglongtu

import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'intermixonline'

class IntermixonlineSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["intermixonline.com"]

    def __init__(self, *args, **kwargs):
        super(IntermixonlineSpider, self).__init__(*args, **kwargs)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            if path.find('page=1') != -1:
                continue
            list_urls.append(list_url)
            requests.append(scrapy.Request(list_url, callback=self.parse))
        return requests

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.intermixonline.com'
        items_xpath = '//div[@class="thumbdiv"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.intermixonline.com'
        nexts_xpath = '//*[@class="default"]/span/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Intermixonline'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@itemprop="brand"]/a/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@itemprop="productId"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[len(data) - 1].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        count_xpath = '//*[@id="additionalImages"]/script/@src'
        data = sel.xpath(count_xpath).extract()
        if len(data) != 0:
            content = urllib2.urlopen(data[0].strip()).read()
            img_count = content.count('Intermix') / 2
            imgs_xpath = '//*[@property="og:image"]/@content'
            data = sel.xpath(imgs_xpath).extract()
            img = data[0].strip()
            for i in range(img_count):
                imgs.append(img.replace('?&$625x781$', '_' + str(i + 1) +
                    '?fit=constrain,1&wid=1400&hei=1400&fmt=jpg'))
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@itemprop="standardPrice"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()[len('$'):]
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