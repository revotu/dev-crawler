# -*- coding: utf-8 -*-
# author: tanyafeng

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'charlotterusse'

class CharlotterusseSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["charlotterusse.com"]

    def __init__(self, *args, **kwargs):
        super(CharlotterusseSpider, self).__init__(*args, **kwargs)

    def _find_nexts_from_list_page(self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        totals_xpath = '//*[@class="totalItemsHidden"]/text()'
        totals = int(sel.xpath(totals_xpath).extract()[0])
        mod = totals % 40
        if mod != 0:
            totals = totals / 40 + 1
        else:
            totals = totals / 40

        requests = []
        if (sel.response.url.find('search.cmd?') != -1 and
            sel.response.url.find('page=') == -1):
            for i in range(totals - 1):
                list_url = sel.response.url + '&page=%s&pCount=%s' % (i + 2, totals)
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            if list_url.find('pCount') == -1:
                list_url = list_url + '&pCount=%s' % totals
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.charlotterusse.com'
        items_xpath = '//*[@class="prodTitle"]/h4/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.charlotterusse.com'
        nexts_xpath = '//*[@rel="next"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Charlotterusse'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Charlotterusse'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="lato styleID"]/span/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        des_str = ''
        description_xpath = '//*[@itemprop="description"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            des_str = ''.join(data)

        detail_xpath = '//*[@class="productDetailsTable"]/tr'
        data = sel.xpath(detail_xpath).extract()
        if len(data) != 0:
            item['description'] = des_str + ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        img_set_pattern = re.compile('":\\[(.*?)\\]')
        img_pattern = re.compile('"(.*?)"')
        for line in sel.response.body.split('\n'):
            idx1 = line.find('prodJson')
            if idx1 != -1:
                img_set = img_set_pattern.findall(line)
                for img_line in img_set:
                    match = img_pattern.findall(img_line)
                    for img_str in match:
                        img_url = ('http://s7d9.scene7.com/is/image/'
                            'CharlotteRusse/%s?$s7product$&&fmt=jpg'
                            '&fit=constrain,1&wid=1600&hei=1600' % img_str)
                        imgs.append(img_url)
                break
        if len(imgs) != 0:
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        multi_color_list = []
        color_pattern = re.compile('"stock":true.*?"COLOR_NAME":"(.*?)"')
        for line in sel.response.body.split('\n'):
            idx1 = line.find('VARIANT_ID')
            if idx1 != -1:
                color_match = color_pattern.findall(line)
                for result in color_match:
                    multi_color_list.append(result)
                break
        color_list = set(multi_color_list)
        item['colors'] = list(color_list)

    def _extract_sizes(self, sel, item):
        size_pattern = re.compile(',\["(.*?)"\]')
        lines = sel.response.body.split('\n')
        for i in range(0, len(lines)):
            idx1 = lines[i].find('["COLOR_NAME","SIZE_NAME"]')
            if idx1 != -1:
                i = i + 1
                size_match = size_pattern.findall(lines[i])
                if len(size_match) != 0:
                    size_list = size_match[0].split('","')
                    item['sizes'] = size_list
                break

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//strike/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            idx = data[0].strip().find('$')
            list_price_number = data[0].strip()[idx + 1:]
            item['list_price'] = self._format_price('USD', list_price_number)

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