# -*- coding: utf-8 -*-
# author: huoda

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'ekseption'

class EkseptionSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["ekseption.es"]

    def __init__(self, *args, **kwargs):
        super(EkseptionSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        flag = url.find('perPage=9&')
        if flag != -1:
            url = url.replace('perPage=9', 'perPage=999999&')
        else:
            url = url + '&perPage=999999&VIEW=1'
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.ekseption.es'
        items_xpath = '//div[@id="novedadesIndexItemImage"]/a//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@class="title productTitle"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'ekseption'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@class="productDetailBrandName"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@name="productId"]//@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="productContentDescription"]/span'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        img_xpath = '//*[@class="imageZoom"]/img//@src'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            base_url = 'http://www.ekseption.es'
            imgs = []
            for img in data:
                img = img.replace('s.jpg', 'l.jpg')
                img = base_url + img
                imgs.append(img)
            if len(imgs) != 0:
                item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_xpath = '//select[@class="productOptionSelectValue"]//text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            sizes = []
            for size in data:
                size = size.strip()
                if len(size) != 0:
                    sizes.append(size)
            if len(sizes) != 0:
                item['sizes'] = sizes

    def _extract_price(self, sel, item):
        price_xpath = '//@data-price'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0]
            flag = price_number.find('|')
            flag_end = price_number.find('.', flag + 1)
            if flag_end != -1:
                item['price'] = self._format_price('EUR', \
                    price_number[flag + 1:flag_end + 2])
            else:
                item['price'] = self._format_price('EUR', \
                    price_number[flag + 1:])

    def _extract_list_price(self, sel, item):
        pass



def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
