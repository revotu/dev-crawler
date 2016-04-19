# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline

from scrapy import log

from scrapy.http import FormRequest

from avarsha_spider import AvarshaSpider


_spider_name = 'tradesy'

class TradesySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["tradesy.com"]

    def __init__(self, *args, **kwargs):
        self.email = 'zzhangliangliang@gmail.com'
        self.pwd = '123456'
        self.formdata = {
            'email' : self.email,
            'password' : self.pwd,
            'tradesy_synchronizer' : '8920a2b67369c280a4da2faa1d389ab4'}
        self.header = {
            'cookie' : 'trackingcookieid=20bhj9jtuq1eng14n7dctaliv6; fonts-loaded=1; optimizelyEndUserId=oeu1433727708660r0.535575938411057; _retarGroup=Criteo; _gsid=05db0452-14ec-4f68-b83d-442d64b1e364; _gat=1; _gat_UA-33494172-1=1; _okdetect=%7B%22token%22%3A%2214341720224430%22%2C%22proto%22%3A%22https%3A%22%2C%22host%22%3A%22www.tradesy.com%22%7D; _okbk=cd4%3Dtrue%2Cvi5%3D0%2Cvi4%3D1434172022949%2Cvi3%3Dactive%2Cvi2%3Dfalse%2Cvi1%3Dfalse%2Ccd8%3Dchat%2Ccd6%3D0%2Ccd5%3Daway%2Ccd3%3Dfalse%2Ccd2%3D0%2Ccd1%3D0%2C; _ok=4910-381-10-1388; AKSB=s=1434172110537&r=https%3A//www.tradesy.com/; GA_goal=registration_complete; GA_goal_label=email; PHPSESSID1=s4gnpi4l41jvk0437si01pjjv1; popupLong=1; utm_reg_source=null; utm_reg_campaign=null; utm_reg_medium=null; utm_reg_content=null; kahuna_dev_id=bng3i5yjgt0qs6ob9eigkfvn; optimizelySegments=%7B%22176399860%22%3A%22false%22%2C%22176542143%22%3A%22gc%22%2C%22176552034%22%3A%22direct%22%2C%22506481092%22%3A%22none%22%2C%221906420206%22%3A%22true%22%2C%221917160845%22%3A%22true%22%2C%221922940731%22%3A%22true%22%2C%222364460149%22%3A%22true%22%7D; optimizelyBuckets=%7B%7D; mp_736d21ae76454a6720ccfdfafce30af0_mixpanel=%7B%22distinct_id%22%3A%20%2214dd0d4a9d67b-079d33fcd-6010177f-1fa400-14dd0d4a9d74e0%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%7D; ltkTesting=modal2; cart_guest=s4gnpi4l41jvk0437si01pjjv1; _oklv=1434172568464%2CQPmyUrka6URNJdMV8c1Bc5X3JHNQI0EB; STSD546572=0; STSID546572=181df4b0-e1e9-4a14-b218-bb920ecefaaf; olfsk=olfsk002560546388849616; wcsid=QPmyUrka6URNJdMV8c1Bc5X3JHNQI0EB; hblid=lWlPCxACWl46TTnP8c1Bc5X3JHN0QEHv; _ga=GA1.2.160007820.1433727701; optimizelyPendingLogEvents=%5B%5D',
            'origin' : 'https://www.tradesy.com',
            'referer' : 'https://www.tradesy.com/',
            'user-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36',
            'x-requested-with' : 'XMLHttpRequest'}
        super(TradesySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        requests = FormRequest(
            'https://www.tradesy.com/ajaxlogin',
            formdata=self.formdata,
            headers=self.header,
            callback=self.after_login)
        return [requests]

    def after_login(self, response):
        self.log('Login to tradesy successfully', log.DEBUG)
        requests = []
        for s_url in self.start_urls:
            requests.append(scrapy.Request(url=s_url, callback=self.parse))
        return requests


    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.tradesy.com'
        items_xpath = '//div[@id="right-panel"]//div/div[@class="item"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'https://www.tradesy.com'
        nexts_xpath = '//div[@id="pagination"]/ul//li/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item_is_available = '//div[@class="item_not_available"]/*'
        data = sel.xpath(item_is_available).extract()
        if data != None:
            self.log('Item is No Longer Available', log.DEBUG)
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//meta[@itemprop="name"]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Tradesy'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//meta[@itemprop="brand"]/@content'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//meta[@itemprop="sku"]/@content'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        image_xpath = '//div[@id="product_page_primary_image"]//a/@href'
        data = sel.xpath(image_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//meta[@itemprop="color"]/@content'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = ('//div[@class="product_row product-details clearfix"]'
            '/p[3]/span/a/text()')
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@id="product-prices-wrapper"]'
            '/div/div[@class="current"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@id="product-prices-wrapper"]'
            '/div/div[@class="original"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0][len('$'):].strip()
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

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
