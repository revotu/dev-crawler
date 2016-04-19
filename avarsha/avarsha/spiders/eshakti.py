# -*- coding: utf-8 -*-
# @author: zhangliangliang


import urllib2

import scrapy.cmdline

import json

from avarsha_spider import AvarshaSpider


_spider_name = 'eshakti'

class EshaktiSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["eshakti.com"]

    def __init__(self, *args, **kwargs):
        super(EshaktiSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        category_url = sel.response.url
        idx1 = category_url.find('shop/')
        idx2 = category_url.find('searchproducts.aspx?q=')
        if idx1 != -1:
            cate = category_url[idx1 + len('shop/'):]
            base_url = ('http://www.eshakti.com/ProductHandler.ashx?cate=%s'
                '&startIndex=1&endIndex=10000&viewAll='
                '&price=&color=&fabric=&sorting=Topsellers' % cate)
            request = urllib2.Request(base_url)
            response = urllib2.urlopen(request)
            data = json.loads(response.read())
            if data.get('item') is not None:
                product_list = data['item']['product']
                if product_list is None:
                    return
                requests = []
                for product in product_list:
                    productId = product['Productid']
                    urlName = product['urlName']
                    item_url = 'http://www.eshakti.com/Product/' \
                            + productId + '/' + urlName
                    item_urls.append(item_url)
                    requests.append(scrapy.Request(item_url, \
                        callback=self.parse_item))
            return requests
        elif idx2 != -1:
            page = 1
            query = category_url[idx2 + len('searchproducts.aspx?q='):]
            requests = []
            while True:
                base_url = ('http://104.131.135.183/v0/products?q=%s'
                    '&ref=eshjcjhd7290vt6ctsk2fro93b6bt2cdj9lnd2sg57b&page=%d'
                    '&per_page=28&sort=null&filters=false' % (query, page))
                header = {'Referer' : 'http://www.eshakti.com/search/%s' % query}
                request = urllib2.Request(base_url, headers=header)
                response = urllib2.urlopen(request)
                data = json.loads(response.read())
                total = data.get('total')
                if total is None:
                    break
                results = data['results']
                for result in results:
                    item_url = result['link']
                    item_urls.append(item_url)
                    requests.append(scrapy.Request(item_url, \
                        callback=self.parse_item))
                if int(total) <= 28 * page:
                    break
                page += 1
            return requests


    # can't find next pages for some problems in the website
    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//*[@id="itemTitle"]/text() | '
            '//span[@itemprop="name"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Eshakti'

    def _extract_brand_name(self, sel, item):
        pass

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="pdtitle"]\
            //span[@id="ctl00_ContentPlaceHolder1_lblProductId"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description1_xpath = '//span[@itemprop="description"]/text()'
        description2_xpath = '//div[@class="details"]/ul/*'
        data1 = sel.xpath(description1_xpath).extract()
        data2 = sel.xpath(description2_xpath).extract()
        content = ''
        if len(data1) != 0:
            for line in data1:
                content += line.strip()
        if len(data2) != 0:
            for line in data2:
                content += line.strip()
        item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        for line in sel.response.body.split(','):
            idx1 = line.find('largeimage: \'')
            if idx1 != -1:
                idx2 = line.find('?', idx1)
                img_url = line[idx1 + \
                    len('largeimage: \''):idx2].strip()
                imgs.append(img_url)
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//table[@class="measurement"]/tbody//tr/td[1]/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@id="ctl00_ContentPlaceHolder1_lblPrice"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = data[0].strip().replace('$', 'USD ')

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
