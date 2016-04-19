# -*- coding: utf-8 -*-
# author: huoda

import urllib2
import json

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'alexandermcqueen'

class AlexandermcqueenSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["alexandermcqueen.com"]

    def __init__(self, *args, **kwargs):
        super(AlexandermcqueenSpider, self).__init__(*args, **kwargs)


    def convert_url(self, url):
        if '#' in url:
            url1 = ('http://www.alexandermcqueen.com/yeti/api/'
                'ALEXANDERMCQUEEN_US/searchIndented.json?')
            url2 = '&baseurl=http://www.alexandermcqueen.com/searchresult.asp'
            tab = url[url.find('#') + 1:]
            url = url1 + tab + url2
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        if 'api'in self.start_urls[0]:
            requests = []
            page = urllib2.urlopen(self.start_urls[0]).read()
            data = json.loads(page)
            items = data['ApiResult']['Items']
            base_url = 'http://www.alexandermcqueen.com'
            for itemm in items:
                item_url = base_url + itemm['SingleSelectLink']
                item_urls.append(item_url)
                request = scrapy.Request(item_url, callback=self.parse_item)
                requests.append(request)
            return requests
        else:
            base_url = 'http://www.alexandermcqueen.com/'
            items_xpath = '//div[@class="productInfoContainer"]/a//@href'

            # don't need to change this line
            return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        # don't need to change this line
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//*[@id="descriptionContainer"]//'
            'div[@id="description"]/h1/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'alexandermcqueen'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Alexander McQueen'

    def _extract_sku(self, sel, item):
        flag = sel.response.body.find('google_tag_params.ecomm_prodid = "')
        flag_end = sel.response.body.find('",', flag + 1)
        if (flag != -1) & (flag < flag_end):
            item['sku'] = sel.response.body[flag + 34:flag_end]

    def _extract_description(self, sel, item):
        description_xpath = '//*[@id="description_pane"]/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_image_urls(self, sel, item):
        imgs = []
        img_xpath = '//*[@id="thumbsContainer"]/li/img//@src'
        data = sel.xpath(img_xpath).extract()
        if len(data) != 0:
            for img in data:
                img = img.replace('_8_', '_13r_')
                imgs.append(img)
            if len(imgs) != 0:
                item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        colors = []
        color_xpath = '//*[@class="colorsList"]//img//@title'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            for color in data:
                color = color.strip()
                colors.append(color)
        flag = sel.response.body.find('"RELATEDCOLORS"')
        flag_end = sel.response.body.find('};', flag + 1)
        text = sel.response.body[flag : flag_end ].strip()
        if 'false' in text:
            pass
        else:
            text = text[text.find('[') + 1:-1]
            text = text.split(', ')
            url1 = ('http://www.alexandermcqueen.com/yeti/'
                'Item.API/1.0/ALEXANDERMCQUEEN_US/item/')
            url2 = ('.json?promotion=true&accountNumber='
                '&trackingPartner=&promocode=')
            for colorId in text:
                colorId = colorId[2:-3]
                url = url1 + colorId + url2
                page = urllib2.urlopen(url).read()
                flag = page.find('},"Description":"')
                flag_end = page.find('","', flag + 17)
                color = page[flag + 17:flag_end].strip()
                colors.append(color)
        if len(colors) != 0:
            item['colors'] = colors

    def _extract_sizes(self, sel, item):
        size_xpath = '//*[@class="SizeW"]//span/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            sizes = []
            for size in data:
                size = size.strip()
                if len(size) != 0:
                    sizes.append(size)
            if len(sizes) != 0:
                item['sizes'] = sizes

    def _extract_price(self, sel, item):
        price_xpath = '//*[@class="itemBoxPrice"]//*[@class="priceValue"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()
            item['price'] = self._format_price('USD', price_number)


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
