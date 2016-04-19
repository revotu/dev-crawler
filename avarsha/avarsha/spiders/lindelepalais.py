# -*- coding: utf-8 -*-
# author: huoda

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'lindelepalais'

class LindelepalaisSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["lindelepalais.com"]

    def __init__(self, *args, **kwargs):
        super(LindelepalaisSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.lindelepalais.com'
        items_xpath = '//div[@class="row"]//a[@class="item"]//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = self.start_urls[0]
        nexts_xpath = '//div[@class="pagination"][1]/ul/li/a[@class="arw next"]//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'lindelepalais'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//h2[@itemprop="brand"]//text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        flag = sel.response.url.rfind('/')
        if flag != -1:
            item['sku'] = sel.response.url[flag + 1:]

    def _extract_description(self, sel, item):
        description_xpath = '//p[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@class="base-zoom"]/div[@class="nav-scroller"]//a//@href'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            imgs = []
            base_url = 'http://www.lindelepalais.com'
            for img in data:
                img = base_url + img
                imgs.append(img)
            if len(imgs) != 0:
                item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//div[@class="colori clearfix"]//img//@alt'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//div[@class="taglie clearfix"]/ul/li/label/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][1:].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="strike"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0][1:].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
