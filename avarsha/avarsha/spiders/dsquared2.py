# -*- coding: utf-8 -*-
# author: huoda

import ast
import urllib2
import json

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'dsquared2'

class Dsquared2Spider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["dsquared2.com"]
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(Dsquared2Spider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.dsquared2.com'
        items_xpath = ('//div[@class="overlayItem"]/div'
            '[@class="overlay"]/a//@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        flag = sel.response.body.find('yTos.search = ')
        if flag != -1:
            flag = sel.response.body.find('{', flag)
            flag_end = sel.response.body.find('};', flag)
            if (flag != -1) & (flag < flag_end):
                data = sel.response.body[flag: flag_end + 1]
                dataDict = ast.literal_eval(data)
                pageNum = int(dataDict['totalPages'])
                page = 1
                while page < (pageNum + 1):
                    list_url = 'http://www.dsquared2.com/Search/RenderProducts?'
                    dataDict['page'] = str(page)
                    for key in dataDict:
                        list_url = list_url + key + '=' + dataDict[key] + '&'
                    page += 1
                    list_urls.append(list_url)
                    request = scrapy.Request(list_url, callback=self.parse)
                    requests.append(request)

                # don't need to change this line
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="Title "]/*[@class="value"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'dsquared2'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'dsquared2'

    def _extract_sku(self, sel, item):
        flag = sel.response.body.find('"Cod10":')
        flag_end = sel.response.body.find('","', flag)
        if (flag != -1) & (flag < flag_end):
            item['sku'] = sel.response.body[flag + 9: flag_end]

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="DetailsInfo"]/*[@class="text"]/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_image_urls(self, sel, item):
        img_xpath = '//*[@class="alternativeImages"]//img//@src'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        colors = []
        sizes = []
        siteCode_xpath = '//*[@name="siteCode"]//@value'
        data = sel.xpath(siteCode_xpath).extract()
        if len(data) != 0:
            siteCode = data[0]
        data_url = ('http://www.dsquared2.com/yTos/api/Plugins/ItemPluginApi'
            '/GetCombinations/?siteCode=') + siteCode + '&code10=' + item['sku']
        req = urllib2.Request(data_url)
        req.add_header('User-Agent', self.user_agent)
        page = urllib2.urlopen(req).read()
        data = json.loads(page)
        for color in data['Colors']:
            colors.append(color['Description'])
        if len(colors) != 0:
            item['colors'] = colors
        for size in data['Sizes']:
            sizes.append(size['Description'])
        if len(sizes) != 0:
            item['sizes'] = sizes

    def _extract_sizes(self, sel, item):
        pass
        # put this in function _extract_colors

    def _extract_price(self, sel, item):
        price_xpath = ('//*[@class="itemBoxPrice"]//*[@class="price"]/'
            'span[@itemprop="price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = ('//*[@class="itemBoxPrice"]//*[@class='
                '"discounted price"]/*[@class="value"]/text()')
            list_price_xpath = ('//*[@class="itemBoxPrice"]//'
                '*[@class="full price"]/*[@class="value"]/text()')
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = data[0].strip()
                item['price'] = self._format_price('USD', price_number)
            data = sel.xpath(list_price_xpath).extract()
            if len(data) != 0:
                list_price_number = data[0].strip()
                item['list_price'] = self._format_price('USD', \
                    list_price_number)

    def _extract_list_price(self, sel, item):
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
