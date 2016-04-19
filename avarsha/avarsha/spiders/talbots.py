# -*- coding: utf-8 -*-
# author: wanghaiyi

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = "talbots"

class TalbotsSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["talbots.com"]

    def __init__(self, *args, **kwargs):
        super(TalbotsSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.talbots.com/'
        items_xpath = ('//div[@class="category-product-img"]/a/@href')
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(item_url)
            requests.append(scrapy.Request(item_url, callback=self.parse_item))
        return requests


    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.talbots.com/'
        nexts_xpath = '//li[@class="productTile  "]/@data-next-page-url'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def join_url(self, id):
        url = 'http://talbots.scene7.com/is/image/Talbots/' + id + '?$zoom$'
        return url

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@id="productDetails"]/h1/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('\n+|\r+|\t+|  +')
            data[0] = data_re.sub('', data[0])
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Talbots'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Talbots'

    def _extract_sku(self, sel, item):
        sku_xpath = '//em[@class="productSku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].replace('# ', '')

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desp = ''
        description_xpath = '//div[@class="prodLongDesc"]//p[@class="MsoNormal"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
            data[0] = data_re.sub('', data[0])
            desp += data[0]
        description_xpath = ('//div[@class="prodLongDesc"]//ul/li')
        data = sel.xpath(description_xpath).extract()
        for per in data:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
            per = data_re.sub('', per)
            desp += per
        item['description'] = desp

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        img_ids = []
        mark_start = '<input type="hidden" id="buildAlts" name="buildAlts" value="'
        for line in sel.response.body.split('\n'):
            idx1 = line.find(mark_start)
            if idx1 != -1:
                idx2 = line.find('">', idx1)
                img_ids = line[idx1 + len(mark_start):idx2].split(',')
                for id in img_ids:
                    img_url = self.join_url(id)
                    imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//strong[@class="itemPrice"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0][len('$'):])
        else:
            price_xpath = ('//strong[@class="salePrice"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                item['price'] = self._format_price('USD', data[0][len('$') + 1:])
            else:
                price_xpath = '//input[@name="priceRange"]/@value'
                data = sel.xpath(price_xpath).extract()
                if len(data) != 0:
                    item['price'] = self._format_price('USD', data[0][len('$'):])

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//strong[@class="normalPrice"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            item['list_price'] = self._format_price('USD', data[0][len('$') + 1:])
        else:
            idx1 = sel.response.body.strip('\n')
            idx1 = idx1.strip(' ')
            if idx1.find('originalAmount') != -1:
                idx_num_tmp = idx1.find('originalAmount')
                idx1 = idx1[idx_num_tmp + 27:]
                idx_num2 = idx1.find('customerAmount')
                price_tmp = idx1[:idx_num2 - 13]
                item['list_price'] = self._format_price('USD', price_tmp)

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
