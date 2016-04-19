# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline

from OpenSSL import SSL

from avarsha_spider import AvarshaSpider


_spider_name = 'lyst'

class LystSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["lyst.com"]

    def __init__(self, *args, **kwargs):
        self.method = SSL.OP_NO_SSLv2
        super(LystSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.lyst.com'
        items_xpath = '//a[@class="product-card-image-link"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        parent_url = sel.response.url
        idx = parent_url.find('?')
        base_url = parent_url[0:idx]
        nexts_xpath = '//a[@class="pagination-link hidden-mobile"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="mb0"]/div[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Lyst'

    def _extract_brand_name(self, sel, item):
        shop_owner_xpath = '//*[@itemprop="brand"]/a/text()'
        data = sel.xpath(shop_owner_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = ('//a[@class="image-gallery-main-img-link hidden-mobile"]'
            '/img/@data-product_id')
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//p[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//*[@class="image-gallery-images"]/a/@data-full-image-url'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            imgs = data
        else:
            imgs_xpath = '//*[@class="image-gallery-main-img-link"]/@href'
            data = sel.xpath(imgs_xpath).extract()
            if len(data) != 0:
                imgs = data
        if len(imgs) != 0:
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//*[@class="buy-option-size-inputs"]/label/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            sizes = []
            for line in data:
                if line.strip() != '':
                    sizes.append(line.strip())
            item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="buy-option-sale-price"]/text()'
        price1_xpath = '//div[@class="buy-option-normal-price"]/text()'
        data = sel.xpath(price_xpath).re('\$\d+\.?\d+')
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)
        else:
            data = sel.xpath(price1_xpath).re('\$\d+\.?\d+')
            if len(data) != 0:
                price_number = data[0][len('$'):].strip()
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_list = '//div[@class="buy-option-normal-price"]/del/text()'
        data = sel.xpath(list_price_list).re('\$\d+\.?\d+')
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['list_price'] = self._format_price('USD', price_number)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        free_xpath = '//span[@class="buy-option-free-shipping"]/text()'
        data = sel.xpath(free_xpath).extract()
        if len(data) != 0:
            if data[0] == 'Free shipping':
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
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
