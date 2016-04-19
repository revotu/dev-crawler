# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline

import re

from avarsha_spider import AvarshaSpider


_spider_name = 'couturecandy'

class CouturecandySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["couturecandy.com"]

    def __init__(self, *args, **kwargs):
        super(CouturecandySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.couturecandy.com/'
        items_xpath = '//ul[contains(@id, "Products")]//li/a[1]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.couturecandy.com/'
        nexts_xpath = '//span[@class="rtlftpad"]//a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@id="rightcol"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0][2:].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Couturecandy'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@id="rightcol"]/h1/a/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        for line in sel.response.body.split('\n'):
            idx1 = line.find('Designer Style No')
            if idx1 != -1:
                idx2 = line.find(' ', idx1 + len('Designer Style No'))
                idx3 = line.find('<', idx2)
                item['sku'] = line[idx2:idx3]
                break

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="rightcol"]/ul/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line.strip()
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        for line in sel.response.body.split('\n'):
            idx1 = line.find('var big = \'')
            if idx1 != -1:
                idx2 = line.find('\';', idx1)
                if idx2 != -1:
                    img_url = line[idx1 + len('var big = \''):idx2].strip()
                    imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//div[not(@style) and @class="notmore"]/b/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//input[@name="size0"]/@value'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data
        else:
            sizes = []
            for line in sel.response.body.split('\n'):
                if line[:3] == 'arr':
                    idx1 = line.find('\"')
                    idx2 = line.rfind('\"')
                    if idx1 != -1 and idx2 != -1 and idx1 < idx2:
                        sizes.append(line[idx1 + 1:idx2])
            item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = (
            '//div[@class="notmore" and contains(@style, "")]/b/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = str(
                re.search(re.compile('\d+\.?\d+'), data[0]).group())
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = (
            '//div[@class="notmore" and contains(@style, "")]/b/del/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):]
            item['list_price'] = self._format_price('USD', price_number)

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
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
