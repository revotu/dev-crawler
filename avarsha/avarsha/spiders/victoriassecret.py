# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'victoriassecret'

class VictoriassecretSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["victoriassecret.com", "sp10048b28.guided.ss-omtrdc.net"]
    is_first = True

    def __init__(self, *args, **kwargs):
        super(VictoriassecretSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.victoriassecret.com'
        items_xpath = '//ul[@class="products  column-3"]//li/a/@href'
        items_s_xpath = '//a[@class="ssf"]/@href'
        items_s2_xpath = '//a[@itemprop="url"]/@href'
        item_nodes = sel.xpath(items_xpath).extract()
        if(len(item_nodes) == 0):
            item_nodes = sel.xpath(items_s_xpath).extract()
        if(len(item_nodes) == 0):
            item_nodes = sel.xpath(items_s2_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'https://sp10048b28.guided.ss-omtrdc.net/'
        nexts_xpath = '//li[@class="next"]/a/@href'
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        if(len(nexts) == 0):
            if(self.is_first == False):
                return requests
            self.is_first = False
            count_xpath = '//span[@class="item-count"]/text()'
            count = sel.xpath(count_xpath).extract()
            item_count = 0
            if(len(count) != 0):
                data_re = re.compile(r'(?:<[^<>]+>)|\n+|\r+|\t+| +|Items')
                item_count = int(data_re.sub('', count[0]).strip())
            _count = 180
            while(_count < item_count):
                base_url = sel.response.url
                list_url = (base_url
                    + '/more?increment=180&location='
                    + str(_count) + '&sortby=REC')
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
                _count += 180
        else:
            list_url = nexts[0]
            if list_url.find(base_url) == -1:
                list_url = base_url + list_url
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@itemprop="name"][1]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = "Victoria's Secret"

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//div[@itemprop="name"][1]'
            '/h2[@class="brandname"]/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()
        else:
            item['brand_name'] = "Victoria's Secret"

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="itemNbr"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'(?:<[^<>]+>)|\n+|\r+|\t+|[ ]+')
            item['sku'] = data_re.sub('', data[0]).strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="full"]'
        data = sel.xpath(description_xpath).extract()
        _description = ''
        if len(data) != 0:
            _description = ''.join([_description, data[0]])
        item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_url_xpath = '//ul[@class="alt-views"]//img/@src'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        if(len(data_imgs) != 0):
            for line in data_imgs:
                image_url = ''.join(['https:', line])
                image_url = image_url.replace('63x84', '760x1013')
                imgs.append(image_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="price"]'
        price = sel.xpath(price_xpath).extract()
        if(len(price) != 0):
            line = price[0]
            idx1 = line.find('<p>')
            if(idx1 != -1):
                idx2 = line.find('<br>', idx1 + len('<p>'))
                line = line[idx1 + len('<p>'):idx2]
            idx1 = line.find('<em>')
            if(idx1 == -1):
                idx2 = line.find('-')
                if(idx2 != -1):
                    line = line[:idx2]
            else:
                idx2 = line.find('/$')
                if(idx2 != -1):
                    line = line[:idx1]
                    idx1 = line.find('-')
                    if(idx1 != -1):
                        line = line[:idx1]
                else:
                    idx2 = line.find('</em>')
                    line = line[idx1:idx2]
            data_re = re.compile(
                r'(?:<[^<>]*>)|\n+|\t+|\r+|[a-zA-Z]+|[ /$]|or|Sale|Clearance')
            item['price'] = self._format_price(
                'USD', data_re.sub('', line).strip())

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="price"]'
        list_price = sel.xpath(list_price_xpath).extract()
        _list_price = ''
        if(len(list_price) != 0):
            line = list_price[0]
            idx1 = line.find('Orig.')
            if(idx1 != -1):
                idx2 = line.find('<em>', idx1)
                if(idx2 != -1):
                    line = line[idx1 + len('Orig.'):idx2]
                if(len(line) != 0):
                    idx1 = line.find('-')
                    if(idx1 != -1):
                        line = line[:idx1]
                data_re = re.compile(r'(?:<[^<>]*>)|\n+|\t+|\r+|[ $]')
                _list_price = data_re.sub('', line).strip()
                item['list_price'] = self._format_price('USD', _list_price)

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
