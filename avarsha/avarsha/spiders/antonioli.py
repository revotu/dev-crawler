# -*- coding: utf-8 -*-
# @author: huangjunjie
import re, urllib2, json

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'antonioli'

class AntonioliSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["antonioli.eu"]

    def __init__(self, *args, **kwargs):
        super(AntonioliSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.antonioli.eu'
        items_xpath = '//li[@class="product-item"]/figure/a[1]/@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        base_url = 'https://www.antonioli.eu'
        nexts_xpath = '//span[@class="next"]/a/@href'
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath1 = ('//div[@class="designer-name"]//*/text()')
        data = sel.xpath(title_xpath1).extract()
        if len(data) != 0:
            title = ''.join(data)
            item['title'] = title

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'antonioli'

    def _extract_brand_name(self, sel, item):
        brand_xpath1 = ('//div[@class="designer-name"]/h1/a/text()')
        data = sel.xpath(brand_xpath1).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        url = sel.response.url
        index = url.rfind('/')
        url = url[index:]
        m = re.search(r'\/(?P<sku>.*)#?', url)
        item['sku'] = m.groupdict('sku')['sku']

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@itemprop="name"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            desc = "".join(data)
            item['description'] = desc


    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@id="gallery"]/ul/li/img/@src'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data


    def _extract_colors(self, sel, item):
        color_xpath = '//table[@id="product-properties"]/tbody/tr[@class="even"]/td[2]/text()'
        data = sel.xpath(color_xpath).extract()
        colors = []
        if len(data) != 0:
            colors.append(data[0])
            item['colors'] = colors

    def _extract_sizes(self, sel, item):
        size_xpath = '//select[@class="size-select"]//option/text()'
        data = sel.xpath(size_xpath).extract()
        data = data[1:]
        data_len = len(data)
        sizes = []
        if data_len != 0:
            for i in range(data_len):
                sizes.append(data[i].strip())
            item['sizes'] = sizes


    def _extract_stocks(self, sel, item):
        pass


    def _extract_price(self, sel, item):
        price_xpath0 = ('//span[@itemprop="price"]/text()')
        data = sel.xpath(price_xpath0).extract()
        for tmp in data:
            price = re.sub(r'[\n\t\r ]', '', tmp)
            m = re.search('[$\d,.]+', price.strip())
            if m:
                price = m.group()
                idx = price.strip().find('$')
                price_number = price.strip()[idx + 1:]
                price_number = price_number.replace('.', 'a')
                price_number = price_number.replace(',', '.')
                price_number = price_number.replace('a', ',')
                item['price'] = self._format_price('USD', price_number)
                break

    def _extract_list_price(self, sel, item):
        price_xpath0 = ('//span[@class="base-price span-price-1"]/text()')
        data = sel.xpath(price_xpath0).extract()
        if len(data) != 0:
            data = re.sub(r'[\n\t\r ]', '', data[0])
            m = re.match('[$\d,.]+', data.strip())
            price = m.group()
            idx = price.strip().find('$')
            price_number = price.strip()[idx + 1:]
            price_number = price_number.replace('.', 'a')
            price_number = price_number.replace(',', '.')
            price_number = price_number.replace('a', ',')
            item['list_price'] = self._format_price('USD', price_number)


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
