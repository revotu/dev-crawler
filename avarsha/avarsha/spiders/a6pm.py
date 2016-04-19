# -*- coding: utf-8 -*-
# author: zhujun

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = '6pm'

class A6pmSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["6pm.com"]

    def __init__(self, *args, **kwargs):
        super(A6pmSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if idx1 != -1:
            base_url = 'http://www.6pm.com'
            idx2 = url.find('/', idx1)
            return base_url + url[idx2:]
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.6pm.com'
        items_xpath = '//*[@id="searchResults"]//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.6pm.com'
        nexts_xpath = '//*[@id="resultWrap"]//div[@class="pagination"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="productStage"]/h1/a/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = '6PM'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@id="productStage"]/h1/a[1]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@id="sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][len('SKU: #'):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = (
            '//*[@id="prdInfoText"]/div[@class="description"]/ul')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        for line in sel.response.body.split('\n'):
            idx1 = line.find('filename: \'')
            if idx1 != -1:
                idx2 = line.find('\',', idx1)
                img_url = line[idx1 + len('filename: \''):idx2].strip()
                imgs.append(img_url)
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
        size_list_xpath = '//select[@name="dimensionValues"]/option/text()'
        size_xpath = '//li[@class="dimensions"]/p[@class="note"]/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            size_list = data[1:]
        else:
            size_list = sel.xpath(size_xpath).extract()
        if len(size_list) != 0:
            item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@id="priceSlot"]/div[@class="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@id="priceSlot"]/span[@class="oldPrice"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0][len('MSRP $'):].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        is_free_shipping_xpath = '//*[@id="shipOpts"]/span/text()'
        data = sel.xpath(is_free_shipping_xpath).extract()
        if len(data) != 0 and data[0] == 'Free':
            item['is_free_shipping'] = True

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
