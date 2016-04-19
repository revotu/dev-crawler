# -*- coding: utf-8 -*-
# @author: wanghaiyi

import urllib

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = "topshop"

class TopshopSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["us.topshop.com"]

    def convert_url(self, url):
        if url.find('&') != -1:
            url_tmp = url[:url.find('#')]
            url_tmp2 = url[url.find('&'):]
            url = url_tmp + url_tmp2
        if url.find('~') != -1:
            url_tmp = url[:url.find('~') + 1]
            url_tmp1 = url[url.find('~') + 1:]
            url_tmp2 = urllib.quote(url_tmp1.encode('utf-8'))
            url = url_tmp + url_tmp2
        return url

    def __init__(self, *args, **kwargs):
        super(TopshopSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//ul[@class="product"]/li[@class="product_image"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="pages"]/ul/li[@class="show_next"]/a/@href'
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            if list_url.find('~') != -1:
                url_tmp = list_url[:list_url.find('~') + 1]
                url_tmp1 = list_url[list_url.find('~') + 1:]
                url_tmp2 = urllib.quote(url_tmp1.encode('utf-8'))
                list_url = url_tmp + url_tmp2
            list_url = list_url.replace(' ', '%20')
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//meta[@property="og:description"]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Topshop'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Topshop'

    def _extract_sku(self, sel, item):
        data = sel.response.url[:sel.response.url.rfind('?')]
        data = data[data.rfind('-') + 1:]
        if len(data) != 0:
            item['sku'] = data

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desc_tmp = ''
        description_xpath = '//div[@class="product_description"]'
        data = sel.xpath(description_xpath).extract()
        for i in range(len(data)):
            desc_tmp = desc_tmp + data[i]
        desc_tmp.replace('\n' , '')
        desc_tmp.replace('\t' , '')
        if len(data) != 0:
            item['description'] = desc_tmp.strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_url_list = []
        img_url_tmp = ''
        imgs_xpath = ('//div/div[@class="frame wrapper_product_view"]'
                '/div/a/@href')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            img_url_list.append(data[0])
            img_url_tmp = data[0]
            for i in range(2 , 6):
                img_url_tmp = data[0][:data[0].find('_large')]
                img_url_tmp = img_url_tmp + '_' + str(i) + '_large.jpg'
                img_url_list.append(img_url_tmp)
        item['image_urls'] = img_url_list

    def _extract_colors(self, sel, item):
        color_xpath = '//li[@class="product_colour"]/span/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//select[@class="product_size"]/option/@value'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//li[@class="product_price"]/span/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$', ''))
        else:
            price_list_xpath = '//ul/li[@class="was_price product_price"]/span/text()'
            data = sel.xpath(price_list_xpath).extract()
            if len(data) != 0:
                item['price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_list_price(self, sel, item):
        price_list_xpath = '//ul/li[@class="was_price product_price"]/span/text()'
        data = sel.xpath(price_list_xpath).extract()
        if len(data) != 0:
            item['list_price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        item['is_free_shipping'] = True

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
