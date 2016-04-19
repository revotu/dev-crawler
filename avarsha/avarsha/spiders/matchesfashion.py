# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'matchesfashion'

class MatchesfashionSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["matchesfashion.com"]

    def __init__(self, *args, **kwargs):
        super(MatchesfashionSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.matchesfashion.com'
        items_xpath = '//*[@class="lister__item__image "]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.matchesfashion.com'
        nexts_xpath = '//*[@class="next"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//*[@class="pdp__header hidden-mobile"]/p'
            '[@class="pdp-description"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Matchesfashion'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@class="pdp__header hidden-mobile"]/h3/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="pdp__product-code"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desc_xpath = '//*[@class="scroller-content"]/p'
        data = sel.xpath(desc_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        images_xpath = ('//*[@class="thumbs-gallery"]/div/@data-main'
            '-img-zoom-url')
        data = sel.xpath(images_xpath).extract()
        img_list = []
        if len(data) != 0:
            for img in data:
                img_list.append('http:' + img)
            item['image_urls'] = img_list

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        stocks_xpath = ('//*[@class="pdp__header hidden-mobile"]/p[@class'
            '="pdp-slug"]/text()')
        data = sel.xpath(stocks_xpath).extract()
        if len(data) != 0:
            if data[0].strip() == 'Sold Out':
                item['stocks'] = 0

    def _extract_price(self, sel, item):
        price_xpath = ('//*[@class="pdp__header hidden-mobile"]/p[@class="pdp-'
            'price"]/span[@class="pdp-price__hilite"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[len(data) - 1].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)
        else :
            price_xpath = ('//*[@class="pdp__header hidden-mobile"]/p'
                '[@class="pdp-price"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0].strip()[len('$'):]
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@class="pdp__header hidden-mobile"]/p'
            '[@class="pdp-price"]/strike/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0 :
            list_price_number = data[0][len('$'):].strip()
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