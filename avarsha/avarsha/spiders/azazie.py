# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re

from avarsha_spider import AvarshaSpider


_spider_name = 'azazie'

class AzazieSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["azazie.com"]
    pro_index = 1

    def __init__(self, *args, **kwargs):
        super(AzazieSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.azazie.com'
        items_xpath = '//div[@class="cat-prod-list"]//div[@class="pic"]//a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.azazie.com'
        nexts_xpath = '//a[@class="next"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        item['title'] = 'azazie'

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'azazie'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'azazie'

    def _extract_sku(self, sel, item):
        item['sku'] = 'azazie'

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        item['description'] = 'azazie'

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        pro_suffix = 0
        imgs = []
        img_xpath = '//ul[@id="thumblist"]/li/a/@rel'
        data = sel.xpath(img_xpath).extract()
        for v in data:
            v = v.encode("utf-8")
            if v.find("largeimage: '") >= 0:
                pro_suffix += 1
                if pro_suffix > 1:
                    imgs.append(v[ v.find("largeimage: '") + len("largeimage: '") : -2] + "?" + "_" + str(self.pro_index) + "_" + str(pro_suffix))
                    continue
                imgs.append(v[ v.find("largeimage: '") + len("largeimage: '") : -2] + "?" + str(self.pro_index) + "_" + str(pro_suffix))
        
        img_reg = re.compile(r'\["(.+?).jpg"\]')
        img_set = img_reg.findall(sel.response.body)[1:]
        for v in img_set:
            pro_suffix += 1
            v = "http://dojygcq45t31s.cloudfront.net/upimg/azazie/h/" + self._remove_escape(v) + ".jpg?" + str(self.pro_index) + "_" + str(pro_suffix)
            imgs.append(v)
        
        self.pro_index += 1
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        item['colors'] = ['azazie']

    def _extract_sizes(self, sel, item):
        item['sizes'] = ['azazie']

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        item['price'] = self._format_price('USD', "999")

    def _extract_list_price(self, sel, item):
        item['list_price'] = self._format_price('USD', "999")

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
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
