# -*- coding: utf-8 -*-
# @author: wanghaiyi

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = "fwrd"

class FwrdSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["fwrd.com"]

    user_agent = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/41.0.2227.0 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(FwrdSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.fwrd.com'
        items_xpath = '//li[@class="item altview_item"]/a/@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.fwrd.com'
        nexts_xpath = '//li[@class="pag_next"]/a/@href'
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="product_info"]/h2/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Fwrd'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//div[@class="product_info"]/'
            'h1[@class="designer_brand"]/a/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        data = sel.response.url[:sel.response.url.rfind('/')]
        data = data[data.rfind('/') + 1:]
        if len(data) != 0:
            item['sku'] = data

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="details"]/ul'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//div/div[@class="product_z"]/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//div[@class="color_dd"]/div/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        list_size = []
        size_list_xpath = ('//div[@class="size_dd"]/select[@id="size-select"]'
            '/option/text()')
        data = sel.xpath(size_list_xpath).extract()
        for i in range(len(data) - 1):
            data_tmp = data[i + 1].replace('\t' , '')
            data_tmp = data_tmp.replace('\n' , '')
            data_tmp = data_tmp.replace(' ' , '')
            if data_tmp.find('SoldOut') == -1:
                list_size.append(data_tmp)
        if len(data) != 0:
            item['sizes'] = list_size

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="product_info"]/div/'
            'span[@class="discount_price"]/text()')

        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="product_info"]/div/'
            'span[@class="price"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price = self._format_price('USD', data[0].replace('$', ''))
            item['list_price'] = list_price

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        item['is_free_shipping'] = True

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
