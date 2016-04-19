# -*- coding: utf-8 -*-
# author: huoda

import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'bananarepublic'

class BananarepublicSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["bananarepublic.gap.com"]
    textt = ''
    resource_text = ''

    def __init__(self, *args, **kwargs):
        super(BananarepublicSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        url = url.replace('+', '!2B')
        url1 = (u'http://bananarepublic.gap.com/resources/productSearch/' +
            u'v1/search?isFacetsEnabled=true&pageId=0&cid=')
        url2 = u'&globalShippingCountryCode=us&locale=en_US&'
        url3 = u'&segment=segB&'
        tabs = ''
        flag = url.find('#')
        if flag != -1:
            tabs = url[(flag + 1):]
        flag = url.find('cid=')
        if flag != -1:
            flag_end = url.find('&', flag)
            cid = url[flag + 4:flag_end]
            url = url1 + cid + url2 + tabs + url3
        else:
            flag = tabs.find('#')
            url1 = (u'http://bananarepublic.gap.com/resources' +
                u'/productSearch/v1/')
            url2 = u'?isFacetsEnabled=true&pageId=0&'
            url3 = u'&globalShippingCountryCode=us&locale=en_US&segment=segB&'
            flag = url.find('searchText=')
            flag_end = url.find('&x', flag + 1)
            if flag_end == -1:
                flag_end = url.find('#')
            if flag_end != -1:
                tab = url[flag + 11:flag_end]
            else:
                tab = url[flag + 11:]
            url = url1 + tab + url2 + url3 + tabs
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        if 'cid' in self.start_urls[0]:
            resources = sel.response.body
            self.textt = sel.response.body
            url1 = 'http://bananarepublic.gap.com/browse/product.do?cid='
            url2 = '&vid=1&pid='
            flag = resources.find('"businessCatalogItemId":"')
            cid_end = resources.find('"', flag +
                len('"businessCatalogItemId":"'))
            cid = resources[flag + len('"businessCatalogItemId":"'):cid_end]
            if len(cid) != 7:
                flag = resources.find('"businessCatalogItemId":"', flag + 1)
                cid_end = resources.find('"', flag +
                    len('"businessCatalogItemId":"'))
                cid = resources[flag + len('"businessCatalogItemId":"'):cid_end]
            flag = resources.find('"businessCatalogItemId":"', cid_end + 1)
            while flag != -1:
                data_end = resources.find('"', flag +
                    len('"businessCatalogItemId":"'))
                data = resources[flag +
                    len('"businessCatalogItemId":"'):data_end]
                if len(data) == 9:
                    pid = data
                    item_url = url1 + cid + url2 + pid
                    item_urls.append(item_url)
                    requests.append(scrapy.Request(item_url, \
                        callback=self.parse_item))
                else:
                    cid = data
                flag = resources.find('"businessCatalogItemId":"', data_end + 1)
        else:
            resources = sel.response.body
            self.textt = self.textt + resources
            urlstart = ('http://bananarepublic.gap.com/browse/'
                'product.do?vid=1&pid=')
            flag = resources.find('"businessCatalogItemId":"')
            while flag != -1:
                data_end = resources.find('"', flag +
                    len('"businessCatalogItemId":"'))
                data = resources[flag +
                    len('"businessCatalogItemId":"'):data_end]
                if len(data) == 9:
                    pid = data
                    item_url = urlstart + pid
                    item_urls.append(item_url)
                    requests.append(scrapy.Request(item_url, \
                        callback=self.parse_item))
                flag = resources.find('"businessCatalogItemId":"', data_end + 1)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        requests = []
        url = self.start_urls[0]
        flag = url.find('pageId=')
        flag_end = url.find('&', flag + 1)
        url1 = url[:flag + 7]
        url2 = url[flag_end:]
        pageId = 1
        url = url1 + str(pageId) + url2
        page = urllib2.urlopen(url).read()
        while 'parentBusinessCatalogItemId' in page:
            list_urls.append(url)
            request = scrapy.Request(url, callback=self.parse)
            requests.append(request)
            pageId += 1
            url = url1 + str(pageId) + url2
            page = urllib2.urlopen(url).read()
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        flag = item['url'].find("pid=")
        pid = item['url'][flag + len("pid="):]
        flag = self.textt.find(pid)
        flag1 = self.textt.find('"name":"', flag)
        flag2 = self.textt.find('","', flag1 + len('"name":"'))
        if flag1 != -1 & flag2 != -1:
            item['title'] = self.textt[flag1 + len('"name":"'):flag2]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'BananaRepublic'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'BananaRepublic'

    def _extract_sku(self, sel, item):
        flag = self.textt.find('"' + item['title'] + '"')
        item['sku'] = self.textt[flag - 18:flag - 12]
        url1 = 'http://bananarepublic.gap.com/browse/productData.do?pid='
        url2 = ('&vid=1&scid=&actFltr=false&locale=en_US&international' +
            'ShippingCurrencyCode=&internationalShippingCountryCode=' +
            'us&globalShippingCountryCode=us')
        url = url1 + item['sku'] + url2
        self.resource_text = urllib2.build_opener(\
            urllib2.HTTPCookieProcessor()).open(url).read().strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        flag = self.resource_text.find('(objP.arrayFabricContent,"')
        flag = self.resource_text.find('^,^', flag + 1)
        flag_end = self.resource_text.find('^,^', flag + 1)
        flag_end_ = self.resource_text.find('");', flag_end + 1)
        sep = self.resource_text.find("||", flag)
        if (sep == -1) | (sep > flag_end_):
            temp1 = self.resource_text[(flag + 3):flag_end]
            temp2 = self.resource_text[(flag_end + 3):flag_end_]
            line1 = temp2 + "% " + temp1
        else:
            line1 = ''
            while(sep != -1) & (sep < flag_end_):
                temp1 = self.resource_text[(flag + 3):flag_end]
                temp2 = self.resource_text[(flag_end + 3):sep]
                line1 = line1 + ' ,' + temp2 + "% " + temp1
                sep = self.resource_text.find("||", sep + 1)
                flag = self.resource_text.find('^,^', flag_end + 1)
                flag_end = self.resource_text.find('^,^', flag + 1)
            temp1 = self.resource_text[(flag + 3):flag_end]
            temp2 = self.resource_text[(flag_end + 3):flag_end_]
            line1 = line1 + ',' + temp2 + "% " + temp1
            line1 = line1[2:]
        description_xpath = '//div[@id="tabWindow"]//noscript'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            data = data[0].strip()
            flag_end = data.find(" <br>\r\n\t            <br>")
            flag_start = len('<noscript>')
            des = data[flag_start:flag_end + len(" <br>\r\n\t")]
            des = line1 + des
            item['description'] = des

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        flag = self.resource_text.find("Z': '")
        base_url = 'http://bananarepublic.gap.com'
        while flag != -1:
            flag_end = self.resource_text.find("'", flag + len("Z': '"))
            img_url = self.resource_text[(flag + len("Z': '")):flag_end]
            img_url = base_url + img_url
            imgs.append(img_url)
            flag = self.resource_text.find("Z': '", flag_end)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        colors = []
        flag = self.resource_text.find("objP.StyleColor(")
        while flag != -1:
            flag = flag + len('objP.StyleColor("403489032","')
            flag_end = self.resource_text.find('",', flag + 1)
            color = self.resource_text[flag:flag_end]
            colors.append(color)
            flag = self.resource_text.find("objP.StyleColor(", flag_end)
        item['colors'] = colors

    def _extract_sizes(self, sel, item):
        sizes = []
        number = len(item['colors'])
        flag = self.resource_text.find("objP.SizeInfoSummary(")
        sep = self.resource_text.find('||', flag + 1)
        flag_end = self.resource_text.find(');', flag + 1)
        if (sep == -1) | (sep > flag_end):
            sizes.append('One Size')
        else:
            flag = self.resource_text.rfind('","', sep - 20, sep - 1)
            flag = flag + 3
            flag_end_ = self.resource_text.find('","', sep + 1)

            while(sep != -1) & (sep < flag_end_):
                flag_end = self.resource_text.find('^,^', flag)
                size = self.resource_text[flag:flag_end]
                size_id = self.resource_text[(flag_end + 3):sep]
                num = self.resource_text.count('^' + size_id + '^')
                if num >= number:
                    sizes.append(size)
                flag = sep + 2
                sep = self.resource_text.find('||', flag + 1)
            flag_end = self.resource_text.find('^,^', flag)
            size = self.resource_text[flag:flag_end]
            size_id = self.resource_text[(flag_end + 3):flag_end_]
            num = self.resource_text.count('^' + size_id + '^')
            if num >= number:
                sizes.append(size)
        item['sizes'] = sizes

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        flag = self.textt.find(item['title'])
        flag_start = self.textt.find('priceDisplay">', flag + 1)
        flag_next = self.textt.find('priceDisplay">', flag_start + 1)
        if flag_next == -1:
            flag_next = len(self.textt)
        flag_twoprice = self.textt.find('priceDisplaySale">$', flag + 1)
        if (flag_twoprice != -1) & (flag_twoprice < flag_next):
            flag_end = self.textt.find('</span>', flag_twoprice)
            price_number = self.textt[(flag_twoprice +
                len('priceDisplaySale">$')):flag_end]
            flag = price_number.find('-$')
            if flag != -1:
                price_number = price_number[:flag]
            item['price'] = self._format_price('USD', price_number)
            list_price_flag = self.textt.find('priceDisplayStrike">$', \
                flag_start)
            list_price_end = self.textt.find('</span>', list_price_flag + 1)
            list_price_number = self.textt[(list_price_flag +
                len('priceDisplayStrike">$')):list_price_end]
            flag = list_price_number.find('-$')
            if flag != -1:
                list_price_number = list_price_number[:flag]
            item['list_price'] = self._format_price('USD', list_price_number)
        else:
            flag_end = self.textt.find('</span>', flag_start + 1)
            price_number = self.textt[(flag_start + \
                len('priceDisplay">$')):flag_end]
            flag = price_number.find('-$')
            if flag != -1:
                price_number = price_number[:flag]
            item['price'] = self._format_price('USD', price_number)

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
