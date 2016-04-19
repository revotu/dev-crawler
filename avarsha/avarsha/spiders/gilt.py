# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = "gilt"

class GiltSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["gilt.com"]

    def __init__(self, *args, **kwargs):
        super(GiltSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx_1 = url.find('?')
        idx_2 = url.find('q.start=0')
        if idx_1 == -1:
            url = url + '?q.rows=48&q.start=0'
        elif idx_2 == -1:
            url = url + '&q.rows=48&q.start=0'
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.gilt.com'
        items_xpath = '//a[@class="product-link"]/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        totals_xpath = '//span[@class="total-results"]/text()'
        data = sel.xpath(totals_xpath).extract()
        mod = int(data[0]) % 48
        if mod != 0:
            totals = int(data[0]) / 48 + 1
        else:
            totals = int(data[0]) / 48
        requests = []
        if totals > 1:
            for i in range(totals - 1):
                rep = ('q.start=%d' % ((i + 1) * 48))
                list_url = sel.response.url.replace('q.start=0', rep)
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="product-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Gilt'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@class="brand-name-text"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//input[@id="product-look-id"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//meta[@name="description"]/@content'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_url_list = []
        small_img_xpath = '//li[@class="thumbnail"]/img/@src'
        data = sel.xpath(small_img_xpath).extract()
        for img in data:
            img = img.replace('96x128', 'lg').replace('//', 'http://')
            img_url_list.append(img)
        item['image_urls'] = img_url_list

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        stocks_xpath = '//meta[@itemprop="availability"]/@content'
        data = sel.xpath(stocks_xpath).extract()
        if len(data) != 0 and data[0] == 'SoldOut':
            item['stocks'] = 0

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            idx = price_number.find('-')
            if idx == -1:
                item['price'] = self._format_price('USD', price_number)
            else:
                low_price_number = price_number[:idx].strip()
                high_price_number = price_number[idx + 1:].strip()[len('$'):]
                item['low_price'] = self._format_price('USD', low_price_number)
                item['high_price'] = self._format_price('USD', high_price_number)
                item['price'] = self._format_price('USD', low_price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="product-price-msrp"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()[len('$'):]
            idx = list_price_number.find('-')
            if idx == -1:
                item['list_price'] = self._format_price('USD', list_price_number)
            else:
                list_price_number = list_price_number[idx + 1:].strip()[len('$'):]
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
