# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

import scrapy

from scrapy.settings import Settings

from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = "unique-vintage"

class UniqueVintageSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["unique-vintage.com"]
    def __init__(self, *args, **kwargs):
        self.user_agent = (
            'http://www.unique-vintage.com/clothing/dresses/fit-and-flare.html')
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)
        super(UniqueVintageSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = ''
        items_xpath = '//*[@class="product-name"]//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        base_url = ''
        nexts_xpath = '//*[@class="pages"]//a//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@class="product-name"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Unique-Vintage'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Unique-Vintage'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="product-id"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][len('Item #'):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="box-collateral"]/*'
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
        for line in sel.response.body.split(' '):
            idx1 = line.find('onclick=\"swapImage(\'')
            if idx1 != -1:
                idx2 = line.find('\',', idx1)
                img_url = line[idx1 + \
                    len('onclick=\"swapImage(\''):idx2].strip()
                imgs.append(img_url)
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//table[@class="measurement"]/tbody//tr/td[1]/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//*[@class="price-box"]/'\
            'span[@class="regular-price"]/span[@class="price"]/text()')
        price1_xpath = ('//*[@class="price-box"]/'\
            'p[@class="special-price"]/span[@class="price"]/text()')

        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_num = data[0].strip()[1:].strip()
            item['price'] = self._format_price('USD', price_num)
        else:
            data = sel.xpath(price1_xpath).extract()
            if len(data) != 0:
                price_num = data[0].strip()[1:].strip()
                item['price'] = self._format_price('USD', price_num)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@class="price-box"]'\
            '//span[contains(@id, "old-price")]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_num = data[0].strip()[1:].strip()
            item['list_price'] = self._format_price('USD', price_num)

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
