# -*- coding: utf-8 -*-
# author: huoda

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'boutique1'

class Boutique1Spider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["boutique1.com"]

    def __init__(self, *args, **kwargs):
        super(Boutique1Spider, self).__init__(*args, **kwargs)


    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@class="product_shot"]/a//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//ul[@class="footer_pagination"]/li/a[@class="next"]//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@class="brand_title"]/span[@class="product_name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Boutique1'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@class="brand_title"]/a/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="additional_details"]/p/span/strong/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_description(self, sel, item):
        description_xpath = '//span[@class="copy_details"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            des = ''
            for description in data:
                des += description
            item['description'] = des

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@class="product_thumbnails"]//a//@href'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = 'title/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            flag = data[0].find(item['title'])
            if flag != -1:
                flag_start = data[0].find('-')
                color = item['title'][flag_start + 1:flag].strip()
                colors = []
                colors.append(color)
                item['colors'] = colors

    def _extract_sizes(self, sel, item):
        size_xpath = '//select[@id="sizesSelectBox" and @class="size_selector"]/option/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            sizes = []
            for size in data:
                size = size.strip()
                if 'Select' in size:
                    continue
                else:
                    sizes.append(size)
            if len(sizes) != 0:
                item['sizes'] = sizes

    def _extract_price(self, sel, item):
        price_xpath = '//span[@class="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            item['price'] = self._format_price('USD', price_number[1:])
        else:
            price_xpath = '//span[@class="discount_price"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0].strip()
                item['price'] = self._format_price('USD', price_number[1:])

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@old_price]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()
            item['price'] = self._format_price('USD', list_price_number[1:])


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
