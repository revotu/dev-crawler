# -*- coding: utf-8 -*-
# author: huoda

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'shopthetrendboutique'

class ShopthetrendboutiqueSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["shopthetrendboutique.com", "store.yahoo.com", "search.store.yahoo.net"]

    def __init__(self, *args, **kwargs):
        super(ShopthetrendboutiqueSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        url = sel.response.url
        if url.find('search') == -1:
            CON = True
        else:
            CON = False
        if CON :
            requests = []
            url = sel.response.url
            url = url + '?page=0'
            response = urllib2.urlopen(url)
            page = response.read()
            item_xpath = '//noscript'
            sel_temp = Selector(text=page)
            data = sel_temp.xpath(item_xpath).extract()
            if len(data) != 0:
                data = data[0]
                base_url = "http://www.shopthetrendboutique.com/"
                flag = data.find("href=")
                while flag != -1:
                    flag_end = data.find('">', flag + 1)
                    url = data[flag + len('href="'): flag_end]
                    item_url = base_url + url
                    item_urls.append(item_url)
                    requests.append(scrapy.Request(item_url, \
                        callback=self.parse_item))
                    flag = data.find("href=", flag_end + 1)
            else:
                item_xpath = '//div[@class="name"]/a//@href'
                data = sel_temp.xpath(item_xpath).extract()
                if len(data) != 0:
                    base_url = "http://www.shopthetrendboutique.com/"
                    for item_url in data:
                        item_url = base_url + item_url
                        item_urls.append(item_url)
                        requests.append(scrapy.Request(item_url, \
                            callback=self.parse_item))
            return requests
        else:
            base_url = ''
            items_xpath = '//td[@colspan="2"]//a//@href'

            return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        nexts_xpath = '//center/a//@href'
        base_url = 'http://search.store.yahoo.net/yhst-81269699784480/cgi-bin/'
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//title[1]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Shopthetrandboutique'

    def _extract_brand_name(self, sel, item):
    # difficult to find the brand from the product page, for the brand can only
    # be found in the title
        pass

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="code"]/b/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description1_xpath = '//td[@align="left"and@valign="top"]/div/text()'
        data = sel.xpath(description1_xpath).extract()
        for line in data:
            line = line.strip()
        line1 = ''.join(data)
        line1 = line1.strip()
        description2_xpath = '//td[@align="left"and@valign="top"]/ul'
        data = sel.xpath(description2_xpath).extract()
        if len(data) != 0:
            line2 = data[0]
            item['description'] = line1 + line2
        else:
            item['description'] = line1

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//img[@style="display: none"and@name="insetimg"]//@src'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//select[@name="Color"]/option/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//select[@name="Size"]/option/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price1_xpath = '//div[@class="price-bold"]/text()'
        data = sel.xpath(price1_xpath).extract()
        if len(data) != 0:
            price = data[0]
        else:
            price2_xpath = '//div[@class="sale-price-bold"]/text()'
            data = sel.xpath(price2_xpath).extract()
            if len(data) != 0:
                price = data[0]
        if len(price) != 0:
            flag = price.find("$")
            price_number = price[flag + 1:]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price = data[0]
            flag = price.find('$')
            price_number = price[flag + 1:]
            item['list_price'] = self._format_price('USD', price_number)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        item['is_free_shipping'] = True


def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
