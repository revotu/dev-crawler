# -*- coding: utf-8 -*-
# author: tanyafeng huoda

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'dillards'

class DillardsSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["dillards.com"]
    storeId = ''
    catalogId = ''
    langId = ''
    categoryId = ''
    facet = ''

    def __init__(self, *args, **kwargs):
        super(DillardsSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        if self.feed_type == 'PRODUCT':
            return url
        url1 = 'http://www.dillards.com/shop/DDS_ProductListingView?storeId='
        url2 = '&langId='
        url3 = '&catalogId='
        url4 = ('&requesttype=ajax&resultType=products&pageView=grid&'
            'searchTerm=&pageSize=100&beginIndex=0&orderBy=1&categoryId=')
        url5 = '&facet='
        page = urllib2.urlopen(url).read()
        sel = Selector(text=page)
        storeId_xpath = '//*[@name="storeId"]//@value'
        data = sel.xpath(storeId_xpath).extract()
        if len(data) != 0:
            self.storeId = data[0]
        catalogId_xpath = '//*[@name="catalogId"]//@value'
        data = sel.xpath(catalogId_xpath).extract()
        if len(data) != 0:
            self.catalogId = data[0]
        langId = '//*[@name="langId"]//@value'
        data = sel.xpath(langId).extract()
        if len(data) != 0:
            self.langId = data[0]
        flag = page.find('cmCreatePageviewTag')
        flag = page.find('", "', flag)
        flag_end = page.find(' ",', flag)
        if (flag != -1) & (flag < flag_end):
            self.categoryId = page[flag + 4:flag_end]
        flag = url.find('facet=')
        tag = url[flag + 6:]
        if len(tag) != 0:
            tag = tag.split('|')
            if len(tag) == 1:
                tag = tag[0].split('%7C')
            for select in tag:
                select_xpath = '//*[@id=' + select + ']//@value'
                data = sel.xpath(select_xpath).extract()
                if len(data) != 0:
                    select = data[0].strip()
                    self.facet = self.facet + select + '|'
        url = url1 + self.storeId + url2 + self.langId + url3 + self.catalogId \
            + url4 + self.categoryId + url5 + self.facet
        return url


    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.dillards.com'
        items_xpath = '//*[@class="product-tile"]//a[1]//@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        total_xpath = '//*[@class="hidden-xs"]/text()'
        data = sel.xpath(total_xpath).extract()
        if len(data) != 0:
            data = data[0].strip()
            flag = data.find('of')
            total_number = int(data[flag + 3:])
            total_page = total_number / 100
            if total_page > 0:
                flag = self.start_urls[0].find('beginIndex=')
                url1 = self.start_urls[0][:flag + 11]
                flag2 = self.start_urls[0].find('&', flag)
                url2 = self.start_urls[0][flag2:]
                page = 1
                while page <= total_page:
                    list_url = url1 + str(page * 100) + url2
                    list_urls.append(list_url)
                    request = scrapy.Request(list_url, callback=self.parse)
                    requests.append(request)
                    page += 1
        # don't need to change this line
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@class="product-title"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Dillards'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//*[@class="brand-link pull-right"]//text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            for brand in data:
                brand = brand.strip()
                if len(brand) != 0:
                    if 'Shop All ' in brand:
                        brand = brand[9:]
                    item['brand_name'] = brand

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="sku"]/span/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="panel-body desktop-description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        img_xpath = ('//div[@class="alt-image-list-container"]'
            '//img//@data-fullimage')
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            base_url = 'http://dimg.dillards.com/is/image/DillardsZoom/'
            for img in data:
                img = img.strip()
                img = base_url + img + '?wid=1500'
                imgs.append(img)
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//*[@class="swatch-list"][1]//img//@title'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = '//*[@title="Please select valid size"][1]/option/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            if 'Size' in data:
                data.remove('Size')
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath1 = '//*[@class="price"]/span[@class="price-number"]/text()'
        price_xpath2 = ('//*[@class="price now-price"]/span'
            '[@class="price-number"]/text()')
        data = sel.xpath(price_xpath1).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            flag = price_number.find('-')
            if flag != -1:
                high_price = price_number[flag + 1:].strip()
                item['high_price'] = self._format_price('USD', high_price[1:])
                price_number = price_number[:flag - 1]
                item['low_price'] = self._format_price('USD', price_number[1:])
            price_number = price_number[1:].strip()
            item['price'] = self._format_price('USD', price_number)
        else:
            data = sel.xpath(price_xpath2).extract()
            if len(data) != 0:
                price_number = data[0].strip()
                flag = price_number.find('-')
                if flag != -1:
                    price_number = price_number[:flag - 1]
                price_number = price_number[1:].strip()
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@class="price original-price"]/'
            'span[@class="price-number"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()
            flag = list_price_number.find('-')
            if flag != -1:
                list_price_number = list_price_number[:flag - 1]
            list_price_number = list_price_number[1:].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

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
