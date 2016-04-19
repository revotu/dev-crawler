# -*- coding: utf-8 -*-
# @author: huangjunjie
import re, json, urllib2, urllib, gzip

import scrapy.cmdline

from StringIO import StringIO

from avarsha_spider import AvarshaSpider


_spider_name = 'brownsfashion'

class BrownsfashionSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["brownsfashion.com"]
    headers = {
        'Accept': '*/*',
        'Accept-Language':'en-US;q=1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'
        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 '
        'Safari/537.36',
        'Accept-Encoding': 'gzip'
           }
    def __init__(self, *args, **kwargs):
        super(BrownsfashionSpider, self).__init__(*args, **kwargs)

    def _get_the_items(self, data):
        url = 'http://www.brownsfashion.com/products/_ajax/search'
        i = 1
        item_urls = []
        while i:
            data['page'] = i
            i += 1
            req = urllib2.Request(url, urllib.urlencode(data), self.headers)
            r = urllib2.urlopen(req)
            if r.info().get('Content-Encoding') == 'gzip':
                buf = StringIO(r.read())
                f = gzip.GzipFile(fileobj=buf)
                content = f.read()
            else:
                content = r.read()
            if content.find('class="itm"') == -1:
                break
            else:
                url_list = re.findall(r'data-url="(.*?)"', content)
                item_urls.extend(url_list)
        return item_urls


    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        url = sel.response.url
        base_url = 'http://www.brownsfashion.com'
        categorySlug_index = url.find('products/')
        if  categorySlug_index != -1:
            index0 = url.find('products/search/')
            if  index0 != -1:
                searchTerms = url[index0 + len('products/search/'):]
                searchTerms = urllib2.unquote(searchTerms)
                data = {'searchTerms':searchTerms}
            else:
                categorySlug = url[categorySlug_index + len('products/'):]
                data = {'categorySlug':categorySlug}
            item_nodes = self._get_the_items(data)
            requests = []
            for path in item_nodes:
                item_url = path
                if path.find(base_url) == -1:
                    item_url = base_url + path
                    item_urls.append(item_url)
                    request = scrapy.Request(item_url, callback=self.parse_item)
                    requests.append(request)
            return requests
        elif url.find('designer') != -1:
            index = url.find('designer/')
            data0 = url[index + len('designer'):]
            data = {}
            m = re.search(r'\/(?P<man>\w*)\/(?P<cate>\w*)#?', data0)
            data['categoryRoot'] = m.groupdict()['cate']
            data['manufacturerName'] = m.groupdict()['man']
            item_nodes = self._get_the_items(data)
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
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//h2[@class="product-manufacturer-name fontFuturaWeight"]'
            '/a/text()|//h5[@class="product-title fontFuturaWeight"]/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            titles = ''.join(data)
            item['title'] = titles


    def _extract_store_name(self, sel, item):
        item['store_name'] = 'brownsfashion'

    def _extract_brand_name(self, sel, item):
        brand_xpath = ('//h2[@class="product-manufacturer-name fontFuturaWeight"]'
            '/a/text()')
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]

    def _extract_sku(self, sel, item):
        url = sel.response.url
        m = re.search(r'product\/(?P<sku>\w*)\/', url)
        if m:
            item['sku'] = m.groupdict('sku')['sku']

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="exBx"]|'
            '//meta[@name="twitter:description"]/@content')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            desc = "".join(data)
            item['description'] = desc


    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//div[@id="gallery-thumbs"]/ul//li//img/@src'
        data = sel.xpath(imgs_xpath).extract()
        for small_img in data:
            large_img_index = small_img.rfind('160x198')
            large_img = small_img[:large_img_index] + 'original' + small_img[large_img_index + len('160x198'):]
            imgs.append(large_img)

        item['image_urls'] = imgs


    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_xpath = ('//div[@style="font-size: 14px; margin: 10px 0 0 0;"]'
            '//label/text()|'
            '//div[@style="font-size: 14px; margin: 10px 0 0 0;"]'
            '//span[@class="p_oos"]/text()')
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _transform(self, data):
        result = {}
        result['price'] = data[1]
        cur = data[0].encode('utf8')
        if  cur.find('$') != -1:
            result['Currency'] = 'USD'
        elif cur.find('£') != -1:
            result['Currency'] = 'GBP'
        elif cur.find('€') != -1:
            result['Currency'] = 'EUR'
        elif cur.find('¥') != -1:
            result['Currency'] = 'JPY'
        elif cur.find('₩') != -1:
            result['Currency'] = 'KRW'
        elif cur.find('IDR') != -1:
            result['Currency'] = 'IDR'
        elif cur.find('A$') != -1:
            result['Currency'] = 'UAD'
        elif cur.find('C$') != -1:
            result['Currency'] = 'CAD'
        return self._format_price(result['Currency'], result['price'])

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="p_p currUpdate"]/'
            'span[not(@class="p_pr")]//text()')
        data0 = sel.xpath(price_xpath).extract()
        data = [x for x in data0 if len(x.strip()) != 0]
        if len(data) != 0:
            item['price'] = self._transform(data)
        else:
            price_xpath = '//meta[@property="product:price:amount"]/@content'
            price_number = sel.xpath(price_xpath).extract()[0]
            cur_xpath = '//meta[@property="product:price:currency"]/@content'
            cur = sel.xpath(cur_xpath).extract()[0]
            item['price'] = self._format_price(cur, price_number)




    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="p_p currUpdate"]/'
            'span[@class="p_pr"]//text()')
        data0 = sel.xpath(list_price_xpath).extract()
        data = [x for x in data0 if len(x.strip()) != 0]
        if len(data) != 0:
            item['list_price'] = self._transform(data)


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
