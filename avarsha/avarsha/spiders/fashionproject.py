# -*- coding: utf-8 -*-
# author: huoda

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'fashionproject'

class FashionprojectSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["fashionproject.com"]

    def __init__(self, *args, **kwargs):
        super(FashionprojectSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.fashionproject.com'
        items_xpath = ('//div[@class="item_container"]//'
            'div[@class="item_top"]//@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'https://www.fashionproject.com'
        nexts_xpath = '//span[@class="pager_arrows"][1]/a//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="id_title"]/p/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'fashionproject'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//meta[@property="og:brand"]//@content'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        flag = sel.response.body.find('"sku"')
        flag_end = sel.response.body.find('","', flag + 1)
        if (flag != -1) & (flag_end != -1):
            sku = sel.response.body[flag + 7 : flag_end]
            item['sku'] = sku

    def _extract_colors(self, sel, item):
        flag = sel.response.body.find('","color":"')
        flag_end = sel.response.body.find('"', flag + 12)
        if (flag != -1) & (flag_end != -1):
            color = sel.response.body[flag + 11:flag_end]
            data = []
            data.append(color)
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//div[@class="id_size"]/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            size = []
            data = data[0].strip()
            data = data[5:].strip()
            size.append(data)
            item['sizes'] = size

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="id_price"]/div[@class="fp_price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            item['price'] = self._format_price('USD', price_number[1:])

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="id_price"]/'
            'div[@class="orig_price"]/span/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()
            item['list_price'] = self._format_price('USD', list_price_number[1:])

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@class="id_top_left"]/ul[@id="etalage"]//@src'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            imgs = []
            for img in data:
                img = 'https:' + img
                imgs.append(img)
            item['image_urls'] = imgs

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="details"]/p'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            des = ''
            for line in data:
                des = des + line
            item['description'] = des

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
