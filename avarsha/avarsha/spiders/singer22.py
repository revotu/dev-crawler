# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline

import math

from avarsha_spider import AvarshaSpider


_spider_name = 'singer22'
page = 1

class Singer22Spider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["singer22.com"]

    def __init__(self, *args, **kwargs):
        self.formdata = {'arrParams[results]' : '100',
                      'arrParams[sex]' : 'woman',
                      'arrParams[category_sex]' : 'U',
                      'arrParams[getPriceFilterCounts]' : '1',
                      'arrParams[with_backinstock_flag]' : '1',
                      'arrParams[prodcat_active]' : '1',
                      'arrParams[page]' : '1',
                      'arrParams[category]' : 'whatsnew'}
        self.headers = {'Accept' :  '*/*',
                    'Connection' : 'keep-alive',
                    'Content-Type' : ('application/x-www-form-urlencoded;'
                                     'charset=UTF-8'),
                    'Cookie' : ('NYC1SSID22=qo2l1lus94ui6pt9oceotiksb0; '
                                'singer-popup-email=1;'
                                 '__utma=150281908.1519759027.1430283293.'
                                 '1431510480.1431652005.13; __utmb=150281908.'
                                 '2.10.1431652005; __utmc=150281908;'
                                  '__utmz=150281908.1430283293.1.1.utmcsr'
                                  '=(direct)|utmccn=(direct)|utmcmd=(none)'),
                    'Host' : 'www.singer22.com',
                    'Origin' : 'https://www.singer22.com',
                    'Referer' : 'https://www.singer22.com/whatsnew.html',
                    'User-Agent' : ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                                    'Chrome/42.0.2311.135 Safari/537.36'),
                    'X-Requested-With' : 'XMLHttpRequest'}
        super(Singer22Spider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if idx1 != -1:
            return url[:idx1]
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = 'https://www.singer22.com'
        items_xpath = '//a[@itemprop="url"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        total_item_xpath = '//span[@class="results-count"]/text()'
        total_item = sel.xpath(total_item_xpath).extract()
        if len(total_item) == 0:
            return []
        total_page = int(math.ceil(int(total_item[0]) / 100.0))
        global page
        page = int(self.formdata['arrParams[page]'])
        if page >= total_page:
            return []

        category_str = ''
        str_url = self.start_urls[0]
        idx1 = str_url.find('.com/')
        if idx1 != -1:
            idx2 = str_url.find('.', idx1 + len('.com/'))
            if idx2 != -1:
                category_str += str_url[idx1 + len('.com/'):idx2]
            else:
                idx3 = str_url.find('/', idx1 + len('.com/'))
                if idx3 != -1:
                    category_str += str_url[idx1 + len('.com/'):idx3]
                else:
                    category_str += str_url[idx1 + len('.com/'):]
        if len(category_str) == 0:
            return []
        self.formdata['arrParams[category]'] = category_str
        self.headers['Referer'] = self.start_urls[0]
        requests = []
        while page < total_page:
            page += 1
            self.formdata['arrParams[page]'] = str(page)
            request = scrapy.FormRequest(url = "https://www.singer22.com/pages",
                        callback = self.parse,
                        method = 'POST',
                        headers = self.headers,
                        formdata = self.formdata)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="styleName"]/span[2]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Singer22'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//span[@itemprop="brand"]/span/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//meta[@itemprop="sku"]/@content'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="styleDescriptionWrap"]/div/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        img_xpath = '//a[@id="productMainLink"]/@href'
        imgs_xpath = (
            '//a[@class="revLightbox lightboxEnlarge styleInsetImage"]/@href')
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            imgs.append(data[0])

        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for img_url in data:
                imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_list_xpath = '//div[@class="productColor"]/text()'
        data = sel.xpath(color_list_xpath).extract()
        if len(data) != 0:
            content = []
            for line in data:
                color_str = line.strip()
                if len(color_str) != 0:
                    content.append(color_str)
            item['colors'] = content

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//table[@id="colorsMatrix"]/tr[1]//th/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        pass
        list_price_xpath = '//div[@id="productColors"]/div[2]//div/div/text()'
        data = sel.xpath(list_price_xpath).extract()
        list_price_number = []
        if len(data) != 0:
            price_num = data[0][len('$'):].strip()
            list_price_number = self._format_price('USD', price_num)
            item['list_price'] = list_price_number

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
