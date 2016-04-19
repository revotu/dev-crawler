# -*- coding: utf-8 -*-
# @author: donglongtu


import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'sierratradingpost'

class SierratradingpostSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["sierratradingpost.com"]

    def __init__(self, *args, **kwargs):
        super(SierratradingpostSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.sierratradingpost.com'
        items_xpath = '//*[@class="js-productThumbnail"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.sierratradingpost.com'
        nexts_xpath = '//*[@class="pages"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@class="linkHeavySection"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[len(data) - 1].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Sierratradingpost'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@class="linkHeavySection"]/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="itemNo"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[len(data) - 1].strip()[len('Item #'):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="overviewDescription g12 a 0"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = ('//*[@class="altImage"]/img/@src | '
            '//*[@id="zoom"]/@href')
        data = sel.xpath(img_xpath).extract()
        img_list = []
        if len(data) != 0:
            for img in data:
                img_list.append(img.replace('~60.', '~1500.')
                    .replace('/t_', '/f_'))
            item['image_urls'] = list(set(img_list))

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@id="displayPrice"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            index = data[0].strip().find('$')
            price_number = data[0].strip()[index + 1:]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@class="priceStory"]/span[@class="ourPrice'
            ' oldPrice"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            index = data[0].strip().find('$')
            list_price_number = data[0].strip()[index + 1:]
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