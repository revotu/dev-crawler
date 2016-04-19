# -*- coding: utf-8 -*-
# author: huoda

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'nicolemiller'

class NicolemillerSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["nicolemiller.com"]

    def __init__(self, *args, **kwargs):
        super(NicolemillerSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.nicolemiller.com/'
        items_xpath = '//*[@class="product-name"]//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""


        # don't need to change this line
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="product-name"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'nicolemiller'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'nicole miller'

    def _extract_sku(self, sel, item):
        sku_xpath = '//meta[@property="cap:product_sku"]//@content'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="short-description std"][1]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        # no idea how to scrap other big images. it needs a update.
        img_xpath = '//meta[@property="cap:product_image"]//@content'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        colors = []
        flag = sel.response.body.find('Product.Config')
        flag = sel.response.body.find('({"', flag + 1)
        flag_end = sel.response.body.find('}});', flag + 1)
        text = sel.response.body[flag : flag_end + 4]
        flag = text.find('label":"')
        flag_end = text.find('","', flag + 8)
        data = text[flag + 8: flag_end]
        while data != 'Size':
            if data != 'Color':
                colors.append(data)
            flag = text.find('label":"', flag_end + 1)
            flag_end = text.find('","', flag + 8)
            data = text[flag + 8: flag_end]
        if len(colors) != 0:
            item['colors'] = colors

    def _extract_sizes(self, sel, item):
        sizes = []
        flag = sel.response.body.find('Product.Config')
        flag = sel.response.body.find('({"', flag + 1)
        flag_end = sel.response.body.find('}});', flag + 1)
        text = sel.response.body[flag : flag_end + 4]
        flag = text.find('"label":"Size"')
        flag = text.find('label":"', flag + 10)
        while flag != -1:
            flag_end = text.find('","', flag + 8)
            data = text[flag + 8: flag_end]
            sizes.append(data)
            flag = text.find('label":"', flag_end + 1)
        if len(sizes) != 0:
            item['sizes'] = sizes

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@class="regular-price"]/'
            'span[@class="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            data[0] = data[0].strip()
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = ('//*[@class="special-price"]/'
                'span[@class="price"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                data[0] = data[0].strip()
                price_number = data[0][len('$'):].strip()
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@class="old-price"]/span[@class="price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data[0] = data[0].strip()
            list_price_number = data[0][len('$'):].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
