# -*- coding: utf-8 -*-
# @author: huangjunjie
import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'openingceremony'

class OpeningceremonySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["openingceremony.us"]

    def __init__(self, *args, **kwargs):
        super(OpeningceremonySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.openingceremony.us'
        items_xpath = '//div[@class="productThumb"]/a/@href'
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def _search_page(self, url, list_urls):
        p = re.compile(r'ocsearch.asp.*keyword=(?P<keyword>.*)')
        m = re.search(p, url)
        keyword = m.groupdict('keyword')['keyword']
        if keyword:
            base_url = 'http://www.openingceremony.us'
            list_url1 = base_url \
            + '/ocsearch.asp?mode=ajax&search=true&cat=women&keyword=' \
            + keyword
            list_url2 = base_url \
            + '/ocsearch.asp?mode=ajax&search=true&cat=men&keyword=' \
            + keyword
            requests = []
            list_urls.append(list_url1)
            request = scrapy.Request(list_url1, callback=self.parse)
            requests.append(request)
            list_urls.append(list_url2)
            request = scrapy.Request(list_url2, callback=self.parse)
            requests.append(request)
            if len(requests) != 0:
                return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.openingceremony.us'
        nexts_xpath = '//div[@class="productsTopNav"]/div[@class="pages"]/a/@href'
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        if len(requests) != 0:
            return requests
        else:
            url = sel.response.url
            p = re.compile(r'ocsearch.asp.*keyword=(?P<keyword>.*)')
            m = re.search(p, url)
            if m:
                return self._search_page(url, list_urls)
            else:
                return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="product_right_info"]/strong/a/text()|'
            '//div[@class="product_right_info"]/span[@class="pname"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            title = ""
            for title_part in data:
                title = title + title_part
        item['title'] = title

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'openingceremony'

    def _extract_brand_name(self, sel, item):
        brand_xpath = ('//div[@class="product_right_info"]'
            '/*[@class="lbldesigner"]/a/text()')
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            brand = data[0]
        item['brand_name'] = brand

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@class="smallfont"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            sku = data[0]
            m = re.search(r'\(SKU:(?P<sku>.*)\s\|', sku)
            item['sku'] = m.groupdict('sku')['sku'].strip()


    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[contains(@class,"plproductdetails")]/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            desc = "".join(data)
            if len(desc.strip()) != 0:
                item['description'] = desc
            else:
                 description_xpath = ('//*[contains(@class,"plproductdetails")]'
                    '/div/text()')
                 data = sel.xpath(description_xpath).extract()
                 desc = "".join(data)
                 item['description'] = desc


    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//div[@class="pili"]//img/@src'
        data = sel.xpath(imgs_xpath).extract()
        for small_img in data:
            small_img = small_img.replace('menu_', '')
            imgs.append(small_img)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//ul[@class="ul_SizesColors"]//li'
        data = sel.xpath(color_xpath).extract()
        color = []
        for _color in data:
            m = re.search(r'li_color.*title="(?P<color>.*?)"', _color)
            if m:
                color.append(m.groupdict('color')['color'])
        if len(data) != 0:
            item['colors'] = list(set(color))


    def _extract_sizes(self, sel, item):
        size_xpath = '//ul[@class="ul_SizesColors"]//li'
        data = sel.xpath(size_xpath).extract()
        size = []
        for _size in data:
            m = re.search(r'li_size.*title="(?P<size>.*?)"', _size)
            if m:
                size.append(m.groupdict('size')['size'])
        if len(data) != 0:
            item['sizes'] = list(set(size))

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath0 = ('//div[@class="productprice"]'
            '//span[@style="color: red"]/text()')
        data = sel.xpath(price_xpath0).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = '//*[@class="productprice"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0].strip()[len('$'):]
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="productprice"]/'
            'span[@style="text-decoration: line-through;"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()
            item['list_price'] = self._format_price('USD', list_price_number)
        pass

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
