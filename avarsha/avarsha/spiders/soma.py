# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

from scrapy.selector import Selector

import re

import urllib2

from avarsha_spider import AvarshaSpider


_spider_name = 'soma'

class SomaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["soma.com"]

    def __init__(self, *args, **kwargs):
        super(SomaSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        total_items_xpath = '//div[@class="collectionItems-info"]/@data-total'
        data = sel.xpath(total_items_xpath).extract()
        if len(data) != 0:
            if int(data[0]) <= 36:
                base_url = 'http://www.soma.com'
                items_xpath = ('//div[@id="shelfProducts"]'
                    '//div[contains(@class, "product-capsule")]/a/@href')
                return self._find_items_from_list_page(sel,
                    base_url, items_xpath, item_urls)

        category = re.findall(re.compile('cat\w+'), sel.response.url)
        if category != None and len(category) == 2:
            if len(category) == 2:
                catRule = re.search(re.compile('catRule\w+'), \
                    sel.response.body).group()
                category_url = ('http://www.soma.com/store/product-list/'
                    '?N=0&Nr=AND(flatCat:%s(AND(%s:cat%s))&shCatId=%s&Ns=%s'
                    '_ranking||product.popularityIndex|1&No=0&Nrpp=9000000' % \
                    (category[1], catRule, catRule[len('catRule'):], \
                     category[1], category[1])
                )
            elif category[1] == 'catsales':
                category_url = ('http://www.soma.com/store/product-list/'
                    '?N=0&Nr=AND(OR(product.catalogId%3Acatalog50002)'
                    '%2CCategory_SalePromoClearance%3AsalePromoClearance)'
                    '&isSale=1&Ns=catsales_ranking||salepopularityIndex|1'
                    '&No=0&Nrpp=9000000')
        elif sel.response.url.find('store/sale?N=') != -1:
            match = re.search(re.compile('N=[\d+\+]+'), sel.response.url)
            category_url = ('http://www.soma.com/store/product-list/'
                    '?%s&Nr=AND(OR(product.catalogId%3Acatalog50002)'
                    '%2CCategory_SalePromoClearance%3AsalePromoClearance)'
                    '&isSale=1&Ns=catsales_ranking||salepopularityIndex|1'
                    '&No=0&Nrpp=9000000' % match.group())
        elif sel.response.url.find('store/category') != -1:
            catRule = re.search(re.compile('catRule\w+'), \
                sel.response.body).group()
            match0 = re.search(re.compile('N=[\d+\+]+'), sel.response.url)
            match1 = re.search(re.compile('cat\d+'), sel.response.url)
            category_url = ('http://www.soma.com/store/product-list/?%s&Nr=AND'
                '(flatCat:%s(AND(%s:cat%s))&shCatId=%s&Ns=%s_ranking||'
                'product.popularityIndex|1&No=0&Nrpp=9000000' % \
                (match0.group(), catRule, catRule[len('catRule'):], \
                 match1.group(), match1.group(), match1.group())
            )

        request = urllib2.Request(category_url)
        response = urllib2.urlopen(request)

        pre_all_item_url = 'http://www.soma.com'
        all_item_urls_xpath = '//a[@class="product-name sh-product-link"]//@href'
        sel = Selector(text=response.read())
        all_item_urls = sel.xpath(all_item_urls_xpath).extract()
        requests = []
        for path in all_item_urls:
            if len(path) != 0:
                item_url = pre_all_item_url + path
                item_urls.append(item_url)
                requests.append(scrapy.Request(item_url, \
                    callback=self.parse_item))
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@id="product-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Soma'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'soma'

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@class="style-id-number"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="product-description-inner"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line.strip()
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        pre_url = 'http://www.soma.com'

        img1_xpath = '//ul[@class="alt-images"]//li/img/@data-alt-image-large'
        data = sel.xpath(img1_xpath).extract()
        if len(data) != 0:
            img_url = data[0]
            imgs.append(pre_url + img_url)

        img2_xpath = '//div[@class="default-product-image columns model-shot-wrapper"]/img/@src'
        data = sel.xpath(img2_xpath).extract()
        if len(data) != 0:
            idx = data[0].find('.jpg')
            if idx != -1:
                img_url = data[0][:idx] + '_large.jpg'
                imgs.append(pre_url + img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//ul[@class="swatches"]/li/@data-color-name'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            colors = []
            colors.append(data[0])
            item['colors'] = colors

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//select[@class="product-size"]//option/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            data_len = len(data) / 5
            size_list = []
            for size in data[1:data_len]:
                if size.strip() not in size_list:
                    size_list.append(size.strip())
                else:
                    break
            item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//ul[@class="product-skus"]/li[1]/input/@data-price'
        giftCard_xpath = (
            '//select[contains(@id, "giftCardValues1")]/option[2]/@value')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][1:]
            item['price'] = self._format_price('USD ', price_number)
        else:
            data = sel.xpath(giftCard_xpath).extract()
            if len(data) != 0:
                price_number = data[0]
                item['price'] = self._format_price('USD ', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = (
            '//ul[@class="product-skus"]/li[1]/input/@data-orignal-price')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][1:]
            item['list_price'] = self._format_price('USD ', price_number)

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
