# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'tartcollections'

class TartcollectionsSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["tartcollections.com"]

    def __init__(self, *args, **kwargs):
        super(TartcollectionsSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        if sel.response.url.find('search.php?Search') != -1:
            items_xpath = ('//ul[@class="ProductList List clear"]'\
                '//li/div[@class="ProductDetails"]/p[@class="p-name"]/a/@href')
        else:
            items_xpath = '//ul[@class="ProductList "]//li/div[1]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        if sel.response.url.find('search.php?Search') != -1:
            base_url = 'http://www.tartcollections.com/'
            nexts_xpath = '//ul[@class="PagingList"]//li/a/@href'
            data = sel.xpath(nexts_xpath).extract()
            requests = []
            for path in data:
                idx = path.find('#')
                if idx != -1:
                    list_url = base_url + path[:idx]
                else:
                    list_url = base_url + path
                list_urls.append(list_url)
                requests.append(scrapy.Request(url=list_url, callback=self.parse))
            return requests
        else:
            base_url = ''
            nexts_xpath = '//ul[@class="PagingList"]//li/a/@href'
            return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="ProductDetailsGrid mobile"]'
            '/div[@class="DetailRow"]/h1/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Tartcollections'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//h4[@class="BrandName"]/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@class="VariationProductSKU"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desc_xpath = '//div[@class="ProductDescriptionContainer prodAccordionContent"]/*'
        data = sel.xpath(desc_xpath).extract()
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
        for line in sel.response.body.split(','):
            idx1 = line.find('largeimage\": \"')
            if idx1 != -1:
                idx2 = line.find('\"}', idx1)
                if idx2 != -1:
                    img_url = line[idx1 + len('largeimage\": \"'):idx2].strip()
                    imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//ul[@class="list-horizontal"]//li/label/span/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@class="ProductPrice '
            'VariationProductPrice"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = (
            '//span[@class="ProductPrice RetailPrice"]/strike/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
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
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
