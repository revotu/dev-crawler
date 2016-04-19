# -*- coding: utf-8 -*-
# @author: wanghaiyi

import urllib2

from scrapy.http import FormRequest
import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider



_spider_name = "mango"

class MangoSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["mango.com"]



    def __init__(self, *args, **kwargs):
        super(MangoSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        sel = Selector(text=sel.response.body)

        """parse items in category page"""

        base_url = 'http://shop.mango.com/'
        items_xpath = '//div[@class="searchResultData extras"]/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        gender_xpath = '//input[@id="Form:SVBusc:SVBusc_4:catalogBrand"]/@value'
        gender = sel.xpath(gender_xpath).extract()[0]
        if gender == 'she':
            list_url = "http://shop.mango.com/catalog.faces?state=she_400_US"
        elif gender == 'he':
            list_url = 'http://shop.mango.com/catalog.faces?state=he_400_US'
        else:
            list_url = 'http://shop.mango.com/catalog.faces?state=violeta_400_US'
        num0_xpath = '//option[@selected="selected"]/@value'
        num0 = sel.xpath(num0_xpath).extract()[0]



        requests = []
        list_urls.append(list_url)
        requests.append(scrapy.FormRequest(url=list_url,
            formdata={
                'Form:SVBusc:SVBusc_4:j_id_au:0:select_europa': num0,
                'Form:SVBusc:SVBusc_4:j_id_au:2:select_europa': 'null',  #
                'Form:SVBusc:SVBusc_4:catalogBrand': gender,
                'Form:SVBusc:SVBusc_4:catalogPage': '2',  ######
                'javax.faces.ViewState': 'VSismDtc41INB60ld/+AYI5YjvTS7wifDb9uJBfZuzpcs4LO',  #
                'javax.faces.source': 'Form:SVBusc:SVBusc_4:j_id_bc:scrollButton',
                'javax.faces.partial.execute': 'Form:SVBusc:SVBusc_4:catalogBrand Form:SVBusc:SVBusc_4:catalogSection Form:SVBusc:SVBusc_4:catalogMenus Form:SVBusc:SVBusc_4:catalogPrice Form:SVBusc:SVBusc_4:catalogPage Form:SVBusc:SVBusc_4:catalogPriceOrder',
                'javax.faces.partial.ajax': 'true',
                'javax.faces.partial.render': 'Form:SVBusc:SVBusc_4:j_id_bc:scrollContainer SVPie:panelPiePagina Form:SVBusc:SVBusc_4:catalogPage Form:SVBusc:SVBusc_4:prendasMangoNextPage',
                'javax.faces.behavior.event': 'click'},
                callback=self.parse))
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@itemprop="name"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Mango'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'MANGO'

    def _extract_sku(self, sel, item):
        sku_xpath = '//input[@name="id_producto_hidden"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//span[@itemprop="description"]/span/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_url_list = []
        img_tmp = ''
        imgs_xpath = '//div[@class="scroll_tray"]/table/tr/td/img/@data-src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                img_tmp = data[i][:data[i].rfind('/') - 1]
                img_tmp = img_tmp + '20' + data[i][data[i].rfind('/'):]
                img_url_list.append(img_tmp)
        item['image_urls'] = img_url_list

    def _extract_colors(self, sel, item):
        color_xpath = '//div[@class="round-border"]/img/@title'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/span/text()'
        price_tmp = ''
        data = sel.xpath(price_xpath).extract()
        price_count = 0
        for i in range(len(data)):
            if data[i] == '$':
                price_count += 1
            price_tmp = price_tmp + data[i]
            if price_count == 2:
                price_tmp = ''
                price_count += 1
        if len(data) != 0:
            item['price'] = self._format_price('USD', price_tmp.replace('$', ''))

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@itemprop="price"]/span/text()'
        price_tmp = ''
        data = sel.xpath(list_price_xpath).extract()
        price_count = 0
        for i in range(len(data)):
            if data[i] == '$':
                price_count += 1
            price_tmp = price_tmp + data[i]
            if price_count == 2:
                item['list_price'] = self._format_price('USD', price_tmp.replace('$', ''))
                break


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
