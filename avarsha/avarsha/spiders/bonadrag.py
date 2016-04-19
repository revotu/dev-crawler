# -*- coding: utf-8 -*-
# author: huoda

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'bonadrag'

class BonadragSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["bonadrag.com"]

    def __init__(self, *args, **kwargs):
        super(BonadragSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.bonadrag.com/index.php'
        items_xpath = ('//div[@class="list_tile_item"]/a'
            '[@class="product_title_link"][1]//@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.bonadrag.com/index.php'
        nexts_xpath = '//div[@class="paging"]//a[@class="page"]//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        pass
        # put this in function _extract_brand_name

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'bonadrag'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//*[@id="product_form"]/div'
            '[@class="prodmanufacturer"]/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()
        title_xpath = '//title/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            if 'brand_name' in item:
                item['title'] = data[0].replace(item['brand_name'], ' ')
                item['title'] = item['title'].strip()
            else:
                item['title'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@name="product[id]"]//@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="productdetaildescr"]//p[1]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        img_xpath = ('//div[@id="rolloverthumbs"]//a[@href='
            '"javascript:void(0);"]/img[@border="0"]//@src')
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            imgs = []
            for img in data:
                flag = img.find('&w=75&h=75')
                if flag != -1:
                    img = img[:flag] + '&w=372&h=450'
                    imgs.append(img)
            if len(imgs) != 0:
                item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_xpath = '//*[@class="product_option"]/..//option/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_price(self, sel, item):
        flag = sel.response.body.find('SALE&nbsp;PRICE')
        if flag == -1:
            price_xpath = '//*[@class="productlistprice"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0][1:].strip()
                item['price'] = self._format_price('USD', price_number)
        else:
            flag = sel.response.body.find('$', flag)
            flag_end = sel.response.body.find('</span>', flag)
            price_number = sel.response.body[flag + 1 : flag_end]
            item['price'] = self._format_price('USD', price_number)
            price_xpath = '//*[@class="productlistprice"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0][1:].strip()
                item['list_price'] = self._format_price('USD', price_number)


    def _extract_list_price(self, sel, item):
        pass
        # put this in function _extract_price

    def _extract_is_free_shipping(self, sel, item):
        is_free_shipping_xpath = '//*[@id="shipOpts"]/span/text()'
        data = sel.xpath(is_free_shipping_xpath).extract()
        if len(data) != 0 and data[0] == 'Free':
            item['is_free_shipping'] = True


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
