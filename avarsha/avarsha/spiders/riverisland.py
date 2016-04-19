# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'riverisland'

class RiverislandSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["us.riverisland.com"]

    def __init__(self, *args, **kwargs):
        super(RiverislandSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//*[@class="products-listing"]/li/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//*[@class="paginator"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Riverisland'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Riverisland'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="small-product-code"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()[len('Product no: '):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="description-copy"]/p'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//*[@class="sliderThumbs alts"]/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for img in data:
                imgs.append(img.strip().replace('$AltThumbNail$'
                    '&locale=en', 'wid=1500'))
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//*[@class="right-side"]/div[@class="price"]/span'
            '/text() | //*[@class="right-side"]/div[@class="price"]'
            '/div[@class="sale"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@class="right-side"]/div[@class="price"]'
            '/p[@class="sale-price"]/del/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[len(data) - 1].strip()[len('$'):]
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