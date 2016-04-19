# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'avenue32'

class Avenue32Spider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["avenue32.com"]

    def __init__(self, *args, **kwargs):
        super(Avenue32Spider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.avenue32.com'
        items_xpath = '//h3[@class="description"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//ul[@class="paging"]/li[@class="next"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Avenue32'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = (
            '//p[contains(@class="brand", @itemprop="brand")]/a/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//meta[@itemprop="sku"]/@content'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="product-tabs"]/div/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line.strip()
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//div[@class="MagicScroll"]//a/@href'
        data = sel.xpath(imgs_xpath).extract()
        imgs = []
        if len(data) != 0:
            for line in data:
                img_url = 'http://www.avenue32.com' + line
                imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//li[@class="selected-colour"]/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//select[@title="Size"]//option[not(@class)]/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            size_list = data[1:]
            if len(size_list) != 0:
                item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//meta[@itemprop="price"]/@content'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//p[@class="price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            idx = data[0].find('$')
            if idx != -1 and idx != 0:
                price_number = data[0][idx + 1:].strip()
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

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
