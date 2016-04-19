# -*- coding: utf-8 -*-
# @author: azhen

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'stylebop'

class StylebopSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["stylebop.com"]

    def __init__(self, *args, **kwargs):
        super(StylebopSpider, self).__init__(*args, **kwargs)

#     def init_start_urls(self, start_urls):
#         converted_start_urls = []
#         for url in start_urls:
#             if url.find("#!") != -1:
#                 parts = url.split("#!")
#                 if len(parts) != 2:
#                     continue
#                 else:
#                     # Ended with "page=0" means the "see all" page.
#                     url = "http://www.stylebop.com/search.php?state=1&" + parts[1] + "&page=0"
#             converted_start_urls.append(url)
#         self.start_urls = converted_start_urls

    def convert_url(self, url):
        if url.find("#!") != -1:
            parts = url.split("#!")
            if len(parts) != 2:
                pass
            else:
                # Ended with "page=0" means the "see all" page.
                url = "http://www.stylebop.com/search.php?state=1&" + parts[1] + "&page=0"
        elif url.find("#%21") != -1:
            parts = url.split("#%21")
            if len(parts) != 2:
                pass
            else:
                # Ended with "page=0" means the "see all" page.
                url = "http://www.stylebop.com/search.php?state=1&" + parts[1] + "&page=0"
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//*[@id="products"]/div[@class="search_break"]/div/a[@class="search_thumb_link"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        self_url = sel.response.url
        # Ended with "page=0" means the "see all" page.
        if (self_url.find("menu") != -1) and (self_url.find("page=0") != -1):
            # I think this is a see all page, return nothing.
            return []

        response_body = sel.response.body
        query_beginning = "var defaultQueryString = '??"
        first_part_pos = response_body.find(query_beginning)
        if first_part_pos == -1:
            # OK, I guess there is no next page.
            return []
        query_part = response_body[first_part_pos + len(query_beginning) :]
        end_pos = query_part.find("'")
        if end_pos == -1:
            # I guess my code has a bug
            return []
        query_part = query_part[:end_pos]

        see_all_url = 'http://www.stylebop.com/search.php?state=1&' + query_part + '&page=0'
        requests = []
        list_urls.append(see_all_url)
        requests.append(scrapy.Request(see_all_url, callback=self.parse))
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@class="Text5"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Stylebop'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@id="productInfo"]/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@style="color: #000"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_part1_xpath = '//*[@id="product_details_data"]/table/tr/td[2]/text()'

        data1 = sel.xpath(description_part1_xpath).extract()
        for data in data1:
            if item.get('description', None) is None:
                item['description'] = data
            else:
                item['description'] += data
        description_part2_xpath = '//*[@id="product_material"]/table/tr/td/table/tr/td[2]/text()'
        data2 = sel.xpath(description_part2_xpath).extract()
        for data in data2:
            if item.get('description', None) is None:
                item['description'] = data
            else:
                item['description'] += data

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//li[@class="image_click_rotator"]/div/a/@href'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = []
            for img_href in data:
                parts = img_href.split("'")
                if len(parts) < 3:
                    break
                url = parts[1]
                if url.find("http://www.stylebop.com") == -1:
                    url = "http://www.stylebop.com" + url
                item['image_urls'].append(url)

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//div[@id="product_size"]/select//option/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) > 1:
            item['sizes'] = data[1:]

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@id="product_price"]/span/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = '//*[@id="product_price"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0].strip()[len('$'):]
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
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

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
