# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'blueandcream'

class BlueandcreamSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["blueandcream.com"]

    def __init__(self, *args, **kwargs):
        super(BlueandcreamSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//h2[@class="product-link"]/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="paginate paginate-top hidden-xs"]//a/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h2[@class="designers text-center"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Blue Cream'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Blue Cream'

    def _extract_sku(self, sel, item):
        _sku = ''
        for line in sel.response.body.split('\n'):
            idx1 = line.find('purple_cloud_product_sku = "')
            if(idx1 != -1):
                idx2 = line.find('"', idx1 + len('purple_cloud_product_sku = "'))
                _sku = line[idx1 + len('purple_cloud_product_sku = "'):idx2]
        item['sku'] = str(_sku)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="info wrapper open"]/div'
        data = sel.xpath(description_xpath).extract()
        _description = ''
        if len(data) != 0:
            _description = ''.join([_description, data[0]])
        item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        base_url = 'http://www.blueandcream.com/mm5/'
        imgs_url_xpath = '//div[@id="product-gallery"]//a/@href'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        if(len(data_imgs) != 0):
            for line in data_imgs:
                image_url = ''.join([base_url, line])
                imgs.append(image_url)
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="name-price"]/h3//span/text()'
        price = sel.xpath(price_xpath).extract()
        if(len(price) != 0):
            for line in price:
                if(line.find('$') != -1):
                    data_re = re.compile(r'\n+|\t+|\r+|[ $]')
                    item['price'] = self._format_price(
                        'USD', data_re.sub('', line).strip())
                    break

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="name-price"]/h3/strike/text()'
        list_price = sel.xpath(list_price_xpath).extract()
        if(len(list_price) != 0):
            data_re = re.compile(r'\n+|\t+|\r+|[ $]')
            item['list_price'] = self._format_price(
                'USD', data_re.sub('', list_price[0]).strip())

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
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
