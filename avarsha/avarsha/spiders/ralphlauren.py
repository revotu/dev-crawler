# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'ralphlauren'

class RalphlaurenSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["ralphlauren.com"]

    def __init__(self, *args, **kwargs):
        super(RalphlaurenSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        base_url = 'http://www.ralphlauren.com'
        _url = sel.response.url
        idx = _url.find('/search/')
        if(idx != -1):
            items_xpath = '//a[@class="prodtitle"]/@href'
            item_nodes = sel.xpath(items_xpath).extract()
        else:
            items_xpath = '//a[@class="brand-link"]/@href'
            item_nodes = sel.xpath(items_xpath).extract()
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            if(item_url.find(' ') != -1):
                item_url = item_url.replace(' ', '%20')
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        base_url = 'http://www.ralphlauren.com/'
        _url = sel.response.url
        idx = _url.find('/search/')
        list_url = ''
        if(idx != -1):
            nexts_xpath = '//a[@class="results next-page"]/@href'
            nexts = sel.xpath(nexts_xpath).extract()
            for path in nexts:
                if(path.find('../') != -1):
                    path = path.replace('../', '')
                list_url = path
                if path.find(base_url) == -1:
                    list_url = base_url + path
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
        else:
            current_page = 0
            next_page = 0
            current_page_xpath = "//input[@class='current-page']/@value"
            data = sel.xpath(current_page_xpath).extract()
            if(len(data) != 0):
                current_page = int(data[0])
            _url = sel.response.url
            idx1 = _url.find('&pg=')
            if(idx1 != -1):
                nexts_xpath = '//a[@class="results"]/@href'
                nexts = sel.xpath(nexts_xpath).extract()
                if(len(nexts) != 0):
                    list_url = nexts[0]
                idx1 = list_url.find('&pg=')
                next_page_str = list_url[idx1 + len('&pg='):]
                if(next_page_str.isdigit()):
                    next_page = int(next_page_str)
                if(next_page <= current_page):
                    list_url = ''
            else:
                list_url = _url + '&pg=' + '2'
            if(list_url != ''):
                if(list_url.find('../') != -1):
                    list_url = list_url.replace('../', '')
                if list_url.find(base_url) == -1:
                    list_url = base_url + list_url
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="prod-summary"]'
            '/div[@itemprop="name"]/h1/text()')
        title2_xpath = '//h3[@class="title"]/text()'
        title3_xpath = '//font[@class="cyoMono_prodTitleLarge"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        data2 = sel.xpath(title2_xpath).extract()
        data3 = sel.xpath(title3_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()
        if len(data2) != 0:
            item['title'] = data2[0].strip()
        if len(data3) != 0:
            item['title'] = data3[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Ralphlauren'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Ralphlauren'

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@itemprop="productID"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +')
            item['sku'] = str(data_re.sub('', data[0]))

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description1_xpath = '//div[@id="longDescDiv"]/p'
        description2_xpath = '//div[@class="detail"]/ul'
        description3_xpath = '//p[@class="description"]'
        description4_xpath = '//div[@class="moreDetailsPDP"]/ul'
        description5_xpath = '//span[@itemprop="description"]'
        data1 = sel.xpath(description1_xpath).extract()
        data2 = sel.xpath(description2_xpath).extract()
        data3 = sel.xpath(description3_xpath).extract()
        data4 = sel.xpath(description4_xpath).extract()
        data5 = sel.xpath(description5_xpath).extract()
        _description = ''
        if len(data1) != 0:
            _description = ''.join([_description, data1[0]])
        if len(data2) != 0:
            _description = ''.join([_description, data2[0]])
        if len(data3) != 0:
            _description = ''.join([_description, data3[0]])
        if len(data4) != 0:
            _description = ''.join([_description, data4[0]])
        if len(data5) != 0:
            _description = ''.join([_description, data5[0]])
        item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        _img_par = ""
        img_url = ""
        imgstr1 = "http://s7d2.scene7.com/is/image/PoloGSI/"
        imgstr2 = "?wid=2000&hei=2000"
        for line in sel.response.body.split('\n'):
            idx1 = line.find('altImages.product')
            if idx1 != -1:
                idx2 = line.find('zoom: \'', idx1)
                while(idx2 != -1):
                    idx3 = line.find('\'', idx2 + len('zoom: \''))
                    _img_par = line[idx2 + len('zoom: \''):idx3].strip()
                    img_url = "".join([imgstr1, _img_par, imgstr2])
                    imgs.append(img_url)
                    line = line[idx3:]
                    idx2 = line.find('zoom: \'')
                idx = _img_par.rfind("_");
                if(idx != -1):
                    _img_par = _img_par[:idx]
                    _img_par = "_lifestyle".join([_img_par, ""])
                    img_url = "".join([imgstr1, _img_par, imgstr2])
                    imgs.append(img_url)
        if(imgs == []):
            for line in sel.response.body.split('\n'):
                idx1 = line.find('&sku=')
                if idx1 != -1:
                    idx2 = line.find('";', idx1)
                    img_url = imgstr1 + line[idx1 + len('&sku='):idx2] + imgstr2
                    imgs.append(img_url)
                idx1 = line.find("zoom: '")
                if idx1 != -1:
                    idx2 = line.find("'", idx1)
                    img_url = (
                        imgstr1 + line[idx1 + len("zoom: '"):idx2] + imgstr2)
                    imgs.append(img_url)
        if(imgs == []):
            img_xpath = '//img[@name="itempic"]/@src'
            data = sel.xpath(img_xpath).extract()
            if(len(data) != 0):
                img_url = data[0]
                imgs.append(img_url)
        item['image_urls'] = list(set(imgs))

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="prod-price"]//'
            'span[@itemprop="price"]/text()')
        price2_xpath = ('//span[@itemprop="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        data2 = sel.xpath(price2_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'\r+|\n+|\t+|$|&#036;')
            item['price'] = self._format_price(
                'USD', data_re.sub('', data[0]).replace('$', ''))
        elif len(data2) != 0:
            data_re = re.compile(r'\r+|\n+|\t+|$|&#036;')
            item['price'] = self._format_price(
                'USD', data_re.sub('', data2[0]).replace('$', ''))

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="prod-price"]/'
            'span[@class="reg-price is-sale"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'\r+|\n+|\t+|$|&#036;')
            item['list_price'] = self._format_price(
                'USD', data_re.sub('', data[0]).replace('$', ''))

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
