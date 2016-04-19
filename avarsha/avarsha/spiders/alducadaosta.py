# -*- coding: utf-8 -*-
# author: huoda

import urllib2

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider



_spider_name = 'alducadaosta'

class AlducadaostaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["alducadaosta.com"]
    headers = {'Host':'www.alducadaosta.com',
        'Cookie':'geoLoc=id=237&nome=USA; TassoCambio=IsoTassoCambio=USD'}
    host = 'www.alducadaosta.com'
    cookie = 'geoLoc=id=237&nome=USA; TassoCambio=IsoTassoCambio=USD'

    def __init__(self, *args, **kwargs):
        super(AlducadaostaSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('Host', self.host)
        settings.set('Cookie', self.cookie)

    def set_crawler(self, crawler):
        super(AlducadaostaSpider, self).set_crawler(crawler)
        crawler.settings.set('Host', self.host)
        crawler.settings.set('Cookie', self.cookie)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.alducadaosta.com'
        items_xpath = '//a[@class="single-product"]//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def _find_items_from_list_page(self, sel, base_url, items_xpath, item_urls):
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(item_url)
            request = scrapy.Request(item_url, headers=self.headers, \
                callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        base_url_xpath = '//link[@rel="canonical"]//@href'
        data = sel.xpath(base_url_xpath).extract()
        if len(data) != 0:
            base_url = data[0]
        if 'search' in self.start_urls[0]:
            base_url = self.start_urls[0]
            requests = []
            currPage = 2
            list_url = base_url + '&currPage=' + str(currPage)
            page = urllib2.urlopen(list_url).read()
            while 'class="single-product"' in page:
                list_urls.append(list_url)
                request = scrapy.Request(list_url, headers=self.headers, \
                    callback=self.parse)
                requests.append(request)
                currPage += 1
                list_url = base_url + '&currPage=' + str(currPage)
                page = urllib2.urlopen(list_url).read()
            return requests
        else:
            nexts_xpath = '//div[@class="pagination"]//img/..//@href'

            # don't need to change this line
            return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)


    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h3[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'alducadaosta'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@itemprop="brand"]//text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//label[@id="productCode"]/b/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="notes"]/div'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        img_xpath = '//div[@class="details"]//ul[@class="big"]//@href'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//meta[@name="twitter:data2"]//@content'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//div[@class="sizes"]//ul[@data-role="listview"]//text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            sizes = []
            for size in data:
                size = size.strip()
                if len(size) != 0:
                    sizes.append(size)
            if len(sizes) != 0:
                item['sizes'] = sizes

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="info"]//*[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$ '):].strip()
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = '//div[@class="info"]//*[@class="relevant"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                data = data[0].strip()
                price_number = data[len('$ '):].strip()
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="info"]//*[@class="strike"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0][len('$ '):].strip()
            item['list_price'] = self._format_price('USD', list_price_number)


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
