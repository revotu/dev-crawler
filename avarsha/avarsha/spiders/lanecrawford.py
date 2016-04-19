# -*- coding: utf-8 -*-
# @author: wanghaiyi

import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = "lanecrawford"

class LanecrawfordSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["lanecrawford.com"]

    def __init__(self, *args, **kwargs):
        super(LanecrawfordSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.lanecrawford.com/'
        items_xpath = '//a[contains(@class,"product_item")]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url_tmp = sel.response.url[:sel.response.url.rfind('/')]
        base_url = base_url_tmp[:base_url_tmp.rfind('/')]
        base_url2 = base_url_tmp[base_url_tmp.rfind('/'):]
        base_url_xpath = '//link[@rel="canonical"]/@href'
        data = sel.xpath(base_url_xpath).extract()
        requests = []
        num_tmp = 1
        if base_url2.find('default') != -1:
            while True:
                try:
                    list_url = (base_url + '/p_' + str(num_tmp) + base_url2 +
                        '/list.lc?plpMode=&displayOption=')
                    content = urllib2.urlopen(list_url).read()
                except Exception as err1:
                    break
                else:
                    if len(content) >= 500:
                        list_urls.append(list_url)
                        requests.append(scrapy.Request(list_url, callback=self.parse,
                            headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) Apple'
                            'WebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Sa'
                            'fari/537.36', }))
                        num_tmp += 1
                    else:
                        break
        else:
            while True:
                try:
                    list_url = (data[0][:data[0].rfind('/')] + '/p_' + str(num_tmp) +
                        '/list.lc?plpMode=&displayOption=')
                    content = urllib2.urlopen(list_url).read()
                except Exception as err1:
                    break
                else:
                    if len(content) >= 500:
                        list_urls.append(list_url)
                        requests.append(scrapy.Request(list_url, callback=self.parse,
                            headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) Apple'
                            'WebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Sa'
                            'fari/537.36', }))
                        num_tmp += 1
                    else:
                        break
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Lanecrawford'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//a[@class="lc-product-brand"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        sku_xpath = '//code[@restinject="productCode"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desc_tmp = ''
        description_xpath = '//div[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                desc_tmp += data[i]
        description2_xpath = '//ul[@class="text-list"]/li'
        data = sel.xpath(description2_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                desc_tmp += data[i]
        item['description'] = desc_tmp

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):

        imgs_xpath = '//a[@class="lc-product-thumb"]/@href'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_list_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_list_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('US$', ''))

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

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
