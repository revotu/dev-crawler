# -*- coding: utf-8 -*-
# author: huoda

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'shopzoeonline'

class ShopzoeonlineSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["shopzoeonline.com"]

    def __init__(self, *args, **kwargs):
        super(ShopzoeonlineSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if idx1 != -1:
            base_url = 'http://www.6pm.com'
            idx2 = url.find('/', idx1)
            return base_url + url[idx2:]
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.shopzoeonline.com'
        items_xpath = ('//div[@class="dvtProduct"]//'
            'div[@class="dvtTitle"]/a//@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.shopzoeonline.com'
        nexts_xpath = '//*[@align="right"]/a//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="dvtItemInfo"]/span[1]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'shopzoeonline'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@class="product_Title"]//span/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        flag = sel.response.url.find('item')
        if flag != -1:
            flag_end = sel.response.url.find('.', flag)
            item['sku'] = sel.response.url[flag + 4 : flag_end]
        else:
            flag = sel.response.body.find('ecomm_prodid":"')
            if flag != -1:
                flag_end = sel.response.body.find('","', flag)
                item['sku'] = sel.response.body[flag + 15:flag_end]

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="dvtItemInfo4"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_image_urls(self, sel, item):
        imgs = []
        img_xpath = ('//div[@class="dvtScroll"]//a'
            '[@style="cursor: pointer"]//@onclick')
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            for img in data:
                flag = img.find("src = '")
                if flag != -1:
                    flag = flag + 7
                    img = img[flag:-1]
                    imgs.append(img)
            if len(imgs) != 0:
                item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_list_xpath = '//*[@id="colors"]/select/option/text()'
        color_xpath = '//*[@id="colors"]/p[@class="note"]/text()'
        data = sel.xpath(color_list_xpath).extract()
        if len(data) == 0:
            data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//td//*[@class="Stock"]/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@id="dvtPrice"]/span'
            '[@class="dvtPriceLoaderRef"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            if '$ ' in price_number:
                price_number = price_number[2:]
            elif '$' in price_number:
                price_number = price_number[1:]
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = ('//*[@class="special-price"][1]/'
                'span[@class="price"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0].strip()
                if '$ ' in price_number:
                    price_number = price_number[2:]
                elif '$' in price_number:
                    price_number = price_number[1:]
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@class="old-price"][1]/'
            'span[@class="price"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()
            if '$ ' in list_price_number:
                list_price_number = list_price_number[2:]
            elif '$' in list_price_number:
                list_price_number = list_price_number[1:]
            item['list_price'] = self._format_price('USD', list_price_number)

    def _extract_is_free_shipping(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
