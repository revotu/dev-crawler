# -*- coding: utf-8 -*-
# author: huoda

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'montaignemarket'

class MontaignemarketSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["montaignemarket.com"]

    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'

    def __init__(self, *args, **kwargs):
        super(MontaignemarketSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.montaignemarket.com'
        items_xpath = '//div[@class="products_list"]//li[@class="listitem"]/a[@class="product_image"]//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        base_url = 'https://www.montaignemarket.com'
        nexts_xpath = '//p[@class="pagination"][1]/a//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []

        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_url = list_url.strip()
            list_url = list_url.replace(' ', '%20')
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        print 'list', list_urls
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="product_rightcol"]/*[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'montaignemarket'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@class="product_rightcol"]/*[@class="pr_brand"]/a[@itemprop="brand"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="pr_brand"]/span[@itemprop="productID"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_description(self, sel, item):
        description_xpath = '//span[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        img_xpath = '//ul[@class="pr_gallery"]/li//img[@title="click to zoom"]//@onclick'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            imgs = []
            for img in data:
                flag = img.find("('")
                img = img[flag + 2:-2]
                imgs.append(img)
            if len(imgs) != 0:
                item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_xpath = '//select[@name="size"]/option/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_price(self, sel, item):
        price_xpath = '//a[@class="price_switch"]//@title'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0]
            if 'USD' in price_number:
                price_number = price_number[:-4].strip()
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
