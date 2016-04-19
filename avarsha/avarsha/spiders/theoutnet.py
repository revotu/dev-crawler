# -*- coding: utf-8 -*-
# @author: wanghaiyi

import scrapy.cmdline


from avarsha_spider import AvarshaSpider


_spider_name = "theoutnet"

class TheoutnetSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["theoutnet.com"]

    def __init__(self, *args, **kwargs):
        super(TheoutnetSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//a[@class="product-link"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//span[@class="next-page"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@id="product-heading"]/h1'
            '/span[@itemprop="name"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Theoutnet'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@id="product-heading"]/h1/a/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        data = sel.response.url[sel.response.url.rfind('/') + 1:]
        if len(data) != 0:
            item['sku'] = data

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_tmp = ''
        description_xpath = '//*[@id="details-section"]/ul/li/div'
        data = sel.xpath(description_xpath).extract()
        for i in range(len(data)):
            description_tmp += data[i]
        if len(data) != 0:
            item['description'] = description_tmp

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_url_list = []
        img_url_tmp = 'http:'
        imgs_xpath = ('//div[@id="expanded-overlay"]/div/ul/li'
            '/a[@class="lgImageLink"]/@href')
        data = sel.xpath(imgs_xpath).extract()
        for i in range(len(data)):
            img_tmp = img_url_tmp + data[i]
            img_url_list.append(img_tmp)
        item['image_urls'] = img_url_list

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@class="exact-price"]/text() | '
            '//span[@class="price-outnet"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_list_price(self, sel, item):
        data_tmp = ''
        price_list_xpath = '//div[@class="price-original"]/text()'
        data = sel.xpath(price_list_xpath).extract()
        if len(data) != 0:
            data_tmp = data[0][data[0].find('$'):]
            item['list_price'] = self._format_price('USD', data_tmp.replace('$', ''))

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
