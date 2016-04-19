# -*- coding: utf-8 -*-
# author: huoda

import string

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'wetseal'

class WetsealSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["wetseal.com"]


    def __init__(self, *args, **kwargs):
        super(WetsealSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.wetseal.com'
        items_xpath = '//*[@class="name-link"]//@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.wetseal.com'
        nexts_xpath = \
            '//*[@class="pagination"][1]//li[@class="pageview"]//@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="product-col-2  product-detail"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Wetseal'

    def _extract_brand_name(self, sel, item):
        flag = item['url'].find('%E2%84%A2')
        if flag == -1:
            item['brand_name'] = 'Wetseal'
        else:
            start = item['url'].rfind('/', 0, flag - 1)
            item['brand_name'] = item['url'][start + 1:flag]

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@itemprop="productID"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            if data[0].find('SKU') != -1:
                item['sku'] = data[0][len('SKU: #'):]
            else:
                item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//meta[@name="description"]//@content'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_urls = []
        img_url_xpath = '//div[@class="product-thumbnails"]//a//@rel'
        data = sel.xpath(img_url_xpath).extract()
        for img_url in data:
            flag = img_url.find("largeimage:")
            img_url = img_url[flag + 13:-2]
            img_urls.append(img_url)
        if len(img_urls) != 0:
            item['image_urls'] = img_urls

    def _extract_colors(self, sel, item):
        colors = []
        color_xpath = '//ul[@class="swatches Color"]/li//text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            for i in data:
                i = i.strip()
                if len(i) != 0:
                    colors.append(i)
        if len(colors) != 0:
            item['colors'] = colors

    def _extract_sizes(self, sel, item):
        sizes = []
        size_xpath = '//ul[@class="swatches size"]/li[@class="emptyswatch"]//text()'
        data = sel.xpath(size_xpath).extract()
        for i in data:
            i = i.strip()
            if len(i) != 0:
                sizes.append(i)
        if len(sizes) != 0:
            item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = \
            '//div[@id="product-content"]//span[@class="price-sales"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            data = data[0].strip()
            now = data.find('Now')
            if now == -1:
                price_number = data[len('$'):]
            else:
                price_number = data[len('Now $'):]
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = '//div[@class="product-price"]//text()'
            data = sel.xpath(price_xpath).extract()
            for i in data:
                i = i.strip()
                flag = i.find(' - ')
                if flag != -1:
                    low_price = i[1:flag]
                    high_price = i[flag + 4:]
                    item['low_price'] = self._format_price('USD', low_price)
                    item['high_price'] = self._format_price('USD', high_price)

    def _extract_list_price(self, sel, item):
        list_price_xpath = \
            '//div[@id="product-content"]//span[@class="price-standard"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            for line in data:
                was = line.find('Was')
                if was == -1:
                    continue
                else:
                    line = line.strip()
                    list_price_number = line[len('Was $'):]
                    item['list_price'] = \
                        self._format_price('USD', list_price_number)
                    break

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        if 'price' in item:
            if string.atof(item['price'][len('USD ')]) > 50:
                item['is_free_shipping'] = True
            else:
                item['is_free_shipping'] = False
        else:
            if 'high_price' in item:
                if string.atof(item['high_price'][len('USD ')]) > 50:
                    item['is_free_shipping'] = True
                else:
                    item['is_free_shipping'] = False

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
