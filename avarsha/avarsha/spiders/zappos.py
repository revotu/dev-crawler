# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'zappos'

class ZapposSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["zappos.com"]
    is_first = True

    def __init__(self, *args, **kwargs):
        super(ZapposSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        if(idx1 != -1):
            idx2 = url.find('/', idx1)
            _var = url[idx2:]
            if(_var.find('?') == -1):
                url = ('http://www.zappos.com' + _var
                    + '?redirect=false&partial=true')
            else:
                url = ('http://www.zappos.com' + _var
                    + '&redirect=false&partial=true')
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.zappos.com'
        items_xpath = '//div[@id="searchResults"]//a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        _url = sel.response.url
        base_url = 'http://www.zappos.com'
        idx = _url.find('?')
        if(idx == -1):
            nexts_xpath = '//a[@class="btn secondary arrow pager 1"]/@href'
            nexts = sel.xpath(nexts_xpath).extract()
            for path in nexts:
                list_url = path
                if path.find(base_url) == -1:
                    list_url = base_url + path
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
        else:
            if(self.is_first == False):
                return requests
            self.is_first = False
            requests = self._get_next_urls(
                sel, base_url, list_urls, requests, _url)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//*[@itemprop="name"]/text()')
        title2_xpath = '//*[@class="banner"]/a[2]/text()'
        data = sel.xpath(title_xpath).extract()
        data2 = sel.xpath(title2_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()
        elif len(data2) != 0:
            item['title'] = data2[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Zappos'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//a[@itemprop="brand"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
#         sku_xpath = '//span[@id="sku"]/text()'
#         data = sel.xpath(sku_xpath).extract()
#         if len(data) != 0:
#             data_re = re.compile(' +|SKU')
#             _sku = data_re.sub('', data[0])
#             item['sku'] = str(_sku)
        sku_xpath = '//*[@itemprop="sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@itemprop="description"]//*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_url_xpath = ('//div[@id="angles-vertical"]'
            '/ul[@id="angles-list"]//span/@style')
        imgs_url2_xpath = ('//div[@id="productImages"]/ul//img/@src')
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        data2_imgs = sel.xpath(imgs_url2_xpath).extract()
        if len(data_imgs) != 0:
            for image_url in data_imgs:
                idx1 = image_url.find('(');
                idx2 = image_url.rfind('-MULTIVIEW_THUMBNAILS.jpg');
                image_url = image_url[idx1 + 1:idx2]
                image_url = ''.join([image_url, '-4x.jpg'])
                imgs.append(image_url)
        if(imgs == []):
            if(len(data2_imgs) != 0):
                for image_url in data2_imgs:
                    idx = image_url.rfind('-MULTIVIEW_THUMBNAILS.jpg');
                    image_url = image_url[:idx]
                    image_url = ''.join([image_url, '-4x.jpg'])
                    imgs.append(image_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@id="priceSlot"]/span[@class='
            '"price nowPrice"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|["$]')
            price = data_re.sub('', data[len(data) - 1])
            item['price'] = self._format_price('USD', str(price))

    def _extract_list_price(self, sel, item):
        pass

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        is_free_shipping_xpath = '//p[@class="shipOpts"]/text()'
        data = sel.xpath(is_free_shipping_xpath).extract()
        if(len(data) != 0):
            if(data[0].find('Free') != -1):
                item['is_free_shipping'] = True

    def _extract_review_count(self, sel, item):
        review_count_xpath = '//p[@class="reviewContent"]'
        item['review_count'] = len(sel.xpath(review_count_xpath))

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        sel1 = sel.xpath('//div[starts-with(@class,"review ") or @class="review"]')
        review_content_xpath = 'div/div/div/p[@class="reviewContent"]/text()'
        review_date_xpath = 'li[@class="reviewDate"]/text()'
        review_auther_xpath = 'li[@class="reviewAuthor"]/span[@itemprop="author"]/text()'
        review_rating_xpath = 'div//span[contains(@class,"stars")]/@class'
        review_list = []
        for sel2 in sel1:
            tmp = dict()
            data = sel2.xpath(review_content_xpath).extract()[0]
            tmp['content'] = data
            sel3 = sel2.xpath('div/ul')
            tmp['date'] = sel3.xpath(review_date_xpath).extract()[0]
            tmp['name'] = sel3.xpath(review_auther_xpath).extract()[0].strip()
            data2 = sel2.xpath(review_rating_xpath).extract()
            tmp['rating'] = round(reduce(lambda x, y:x + y, map(lambda x:float(x[-1]), data2)) / 3, 1)
            review_list.append(tmp)
        item['review_list'] = review_list


    def _get_next_urls(self, sel, base_url, list_urls, requests, _url):
        t_num_xpath = '//h1[@id="searchHeaderHeader"]/em[not(@id)]/text()'
        t_num = sel.xpath(t_num_xpath).extract()
        total_num = 0
        if(len(t_num) != 0):
            total_num = int(t_num[0]) / 100
        idx1 = _url.find('/CK')
        idx2 = _url.find('.zso')
        if(idx1 == -1 and idx2 == -1):
            facetBase_xpath = ('//div[@id="sortWrap"]'
                '//a[@class="gae-click*Search-Results-Page*Dropdown-Sort-By'
                '-Lowest-Price*no-term"]/@href')
            _facetBase = sel.xpath(facetBase_xpath).extract()
            facetBase = ''
            if(len(_facetBase) != 0):
                facetBase = _facetBase[0]
                idx1 = facetBase.find('?')
                facetBase = facetBase[:idx1]
            _url = base_url + facetBase
            idx1 = _url.find('/CK')
        var1 = ''
        var2 = ''
        var3 = ''
        _var1 = ''
        _var2 = ''
        _var3 = ''
        idx2 = _url.rfind('?')
        var1 = _url[:idx1] + '-page'
        idx1 = _url.rfind('/CK')
        if(idx1 == -1):
            idx1 = _url.find('.zso') - 1
        if(idx2 != -1):
            var2 = _url[idx1:idx2 + 1] + 'p='
            var3 = '&' + _url[idx2 + 1:]
        else:
            var2 = _url[idx1:] + '?p='
        idx4 = _url.find('-page')
        idx5 = _url.find('p=', idx4)
        idx7 = _url.find('&', idx5)
        page = 1
        while(page <= total_num):
            if(idx4 == -1 and idx5 == -1):
                list_url = var1 + str(page + 1) + var2 + str(page) + var3
            else:
                _va1 = _url[:idx4 + len('-page')]
                if(idx5 != -1):
                    _var2 = _url[idx1:idx5 + len('p=')]
                if(idx7 != -1):
                    _var3 = _url[idx7:]
                list_url = (_va1 + str(page + 1)
                    + _var2 + str(page) + _var3)
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
            page += 1
        return requests
def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
