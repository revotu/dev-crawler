# -*- coding: utf-8 -*-
# author: wanghaiyi

import re

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = "shoptiques"

class ShoptiquesSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["shoptiques.com"]
    user_agent = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/41.0.2227.0 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(ShoptiquesSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.shoptiques.com/'
        items_xpath = ('//p[@itemprop="name"]/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.shoptiques.com/'
        nexts_xpath = '//div[@class="pages"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def add_url(self, img_name):
        img_url = ('http://sugartown.scene7.com/is/image/sugartown/'
            + img_name + '?wid=675&hei=1125')
        return img_url

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@id="product-detail"]/div'
            '[@class="product-name"]/h1/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('\n+|\r+|\t+|  +')
            data[0] = data_re.sub('', data[0])
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Shoptiques'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//span[@itemprop="brand"]/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//a[@id="add-to-cart"]/@unbxdparam_sku'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desp = ''
        description_xpath = ('//div[@class="accordion"]//'
            'div[@id="collapseOne"]//p')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
            for i in range(len(data)):
                if i == 0:
                    data[0] = 'Description'
                else:
                    data[i] = data_re.sub('', data[i])
                desp += data[i]
        item['description'] = desp

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//div[@class="image-gallery"]//img/@data-deferred-large'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            imgs = data
        for img in imgs:
            if img.strip() == '':
                imgs.remove(img)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="product-name"]/span'
            '[@id="product-price"]/span/text()')
        price_two_xpath = '//span[@itemprop="price"]/@content'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0][len('$'):].strip())
        else:
            data = sel.xpath(price_two_xpath).extract()
            if len(data) != 0:
                item['price'] = self._format_price('USD', data[0])

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="retail"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            item['list_price'] = self._format_price('USD', data[0][len('$'):].strip())

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
