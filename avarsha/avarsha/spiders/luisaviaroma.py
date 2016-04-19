# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import types
import time
import urllib2
import lxml.html as HT

import scrapy.cmdline
from scrapy import log
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider
from avarsha.items import ProductItem


_spider_name = 'luisaviaroma'

class LuisaviaromaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["luisaviaroma.com"]
    is_first = True

    def __init__(self, *args, **kwargs):
        super(LuisaviaromaSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        url = urllib2.unquote(url.encode('utf-8'))
        idx = url.find('#')
        if(idx != -1):
            idx1 = url.find('CatalogSrv.ashx|')
            if(idx1 != -1):
                new_line = []
                idx2 = url.find('&PaletteColors', idx1)
                if(idx2 != -1):
                    line = url[idx1 + len('CatalogSrv.ashx|'):]
                    parmts = line.split('&')
                    if(len(parmts) != 0):
                        for var in parmts:
                            one_piece = var.split('=')
                            if(one_piece[1].isdigit()
                               or type(one_piece[1]) is types.BooleanType):
                                new_line.append(
                                    '"' + one_piece[0] + '":' + one_piece[1])
                            else:
                                new_line.append('"'
                                    + one_piece[0] + '":"' + one_piece[1] + '"')
                new_line_encoded = ','.join(new_line)
                _target1 = 'http://www.luisaviaroma.com/CatalogSrv.ashx?data={'
                _target2 = (
                    ',"MaxItemXPage":48,"Page":0,"SortTypeString":"Designer"'
                    ',"ResponseTypeString":"TextToEval"}&time=')
                _time_stamp = str(time.time())
                new_url = ((_target1 + new_line_encoded
                    + _target2 + _time_stamp)
                    .replace(' ', '%20').replace('"', '%22')
                    .replace('[', '%5B').replace(']', '%5D')
                    .replace('{', '%7B').replace('}', '%7D'))
                url = new_url
            elif(url.find('FullTextSearch.aspx') != -1):
                _target1 = ('http://www.luisaviaroma.com'
                    '/FullTextService.axd?data={"SearchText":"')
                _target2 = ('","CountryCode":"US","Language":"EN","PageIndex":1'
                    '}&callback=catalogResponse=&time=')
                _time_stamp = str(time.time())
                _SearchText = ''
                _SeasonContext = ''
                _GenderMemoCode = ''
                _DefaultContext = ''
                idx1 = url.find('FullSearchText=')
                if(idx1 != -1):
                    idx2 = url.find('&season=', idx1)
                    if(idx2 != -1):
                        _SearchText = url[idx1 + len('FullSearchText='): idx2]
                        idx1 = url.find('&gender=', idx2)
                        if(idx1 != -1):
                            _SeasonContext = url[idx2 + len('&season='): idx1]
                            idx2 = url.find('&default=', idx1)
                            if(idx2 != -1):
                                _GenderMemoCode = (
                                    url[idx1 + len('&gender='): idx2])
                                idx1 = url.find('#')
                                if(idx1 != -1):
                                    _DefaultContext = (
                                        url[idx2 + len('&default='): idx1])
                new_url = ((_target1 + _SearchText + '","SeasonContext":"'
                    + _SeasonContext + '","GenderMemoCode":"'
                    + _GenderMemoCode + '","DefaultContext":"'
                    + _DefaultContext + _target2 + _time_stamp)
                    .replace(' ', '%20').replace('"', '%22')
                    .replace('[', '%5B').replace(']', '%5D')
                    .replace('{', '%7B').replace('}', '%7D'))
                url = new_url
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        _url = sel.response.url
        designerId = ''
        paletteColors = ''
        subcategory = ''
        idx1 = _url.rfind('filterDes%22:')
        if(idx1 != -1):
            idx2 = _url.find(',', idx1)
            designerId = _url[idx1 + len('filterDes%22:'):idx2]
        idx1 = _url.rfind('PaletteColors%22:%22')
        if(idx1 != -1):
            idx2 = _url.find('%22,', idx1 + len('PaletteColors%22:%22'))
            paletteColors = _url[idx1 + len('PaletteColors%22:%22'):idx2]
        idx1 = _url.rfind('subcategory%22:')
        if(idx1 != -1):
            idx2 = _url.find(',', idx1 + len('subcategory%22:'))
            subcategory = _url[idx1 + len('subcategory%22:'):idx2]
        requests = self._simplify_item_url(
            sel, designerId, paletteColors, subcategory, item_urls)

        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        if(self.is_first == False):
            return requests
        self.is_first = False
        _url = urllib2.unquote(sel.response.url.encode('utf-8'))
        index = 2
        _PageCount = 0
        line = sel.response.body
        idx1 = line.find('PageCount":')
        if(idx1 != -1):
            idx2 = line.find(',"', idx1)
            _PageCount = int(line[idx1 + len('PageCount":'):idx2])
        idx1 = _url.find('PageIndex":')
        if(idx1 != -1):
            idx2 = _url.find(',"', idx1)
            if(idx2 == -1):
                idx2 = _url.find('}', idx1)
        while(index <= _PageCount):
            list_url = ((_url[:idx1 + len('PageIndex":')]
                + str(index) + _url[idx2:])
                .replace(' ', '%20').replace('"', '%22')
                .replace('[', '%5B').replace(']', '%5D')
                .replace('{', '%7B').replace('}', '%7D'))
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
            index += 1
        return requests

    def parse_item(self, response):
        self.log('Parse item link: %s' % response.url, log.DEBUG)

        if(response.url.find('/lang_EN/') != -1):
            new_item_url = (self._extract_item_url(response.url)
                .replace(' ', '%20').replace('"', '%22')
                .replace('[', '%5B').replace(']', '%5D')
                .replace('{', '%7B').replace('}', '%7D'))
            req = urllib2.Request(new_item_url)
            resbody = urllib2.urlopen(req)
            response = response.replace(body=resbody.read())

        sel = Selector(response)
        item = ProductItem()
        self._extract_url(sel, item)
        self._extract_title(sel, item)
        self._extract_store_name(sel, item)
        self._extract_brand_name(sel, item)
        self._extract_sku(sel, item)
        self._extract_features(sel, item)
        self._extract_description(sel, item)
        self._extract_size_chart(sel, item)
        self._extract_color_chart(sel, item)
        self._extract_image_urls(sel, item)
        self._extract_basic_options(sel, item)
        self._extract_stocks(sel, item)
        self._extract_prices(sel, item)
        self._extract_is_free_shipping(sel, item)
        self._extract_reviews(sel, item)

        self._save_product_id(sel, item)
        self._record_crawl_datetime(item)
        self._save_product_collections(sel, item)

        return item

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        line = sel.response.body
        idx = line.find('ItemTotalLook')
        line = line[:idx]
        idx1 = line.find('ShortDescription":"')
        if(idx1 != -1):
            idx2 = line.find('",', idx1)
            item['title'] = line[idx1 + len('ShortDescription":"'):idx2]

    def _extract_store_name(self, sel, item):
        item['store_name'] = "Luisaviaroma"

    def _extract_brand_name(self, sel, item):
        line = sel.response.body
        idx = line.find('ItemTotalLook')
        line = line[:idx]
        idx1 = -1
        idx = line.find('Designer":{"')
        if(idx != -1):
            idx1 = line.find('Description":"', idx)
        if(idx1 != -1):
            idx2 = line.find('",', idx1)
            item['brand_name'] = line[idx1 + len('Description":"'):idx2]
        else:
            item['brand_name'] = "Luisaviaroma"

    def _extract_sku(self, sel, item):
        line = sel.response.body
        idx = line.find('ItemTotalLook')
        line = line[:idx]
        idx1 = line.find('ItemCode":"')
        if(idx1 != -1):
            idx2 = line.find('"', idx1 + len('ItemCode":"'))
            _sku = line[idx1 + len('ItemCode":"'):idx2]
            item['sku'] = _sku

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        line = sel.response.body
        idx = line.find('ItemTotalLook')
        line = line[:idx]
        idx1 = line.find('LongtDescription":"')
        if(idx1 != -1):
            idx2 = line.find('",', idx1)
            item['description'] = (
                line[idx1 + len('LongtDescription":"'):idx2].replace('|', '\n'))

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        image_url = ''
        base_url = 'http://images.luisaviaroma.com/Zoom'
        line = sel.response.body
        while(True):
            idx1 = line.find('"Path":"')
            if(idx1 != -1):
                idx2 = line.find('",', idx1)
                image_url = base_url + line[idx1 + len('"Path":"'):idx2]
                imgs.append(image_url)
                line = line[idx2:]
            else:
                break
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        line = sel.response.body
        idx = line.find('ItemTotalLook')
        line = line[:idx]
        _CurrencyId = ''
        _FinalPrice = ''
        idx1 = line.find('Prices":[{"CurrencyId":"')
        idx2 = -1
        if(idx1 != -1):
            idx2 = line.find('",', idx1)
            _CurrencyId = line[idx1 + len('Prices":[{"CurrencyId":"'):idx2]
        idx1 = line.find('FinalPrice":', idx2)
        if(idx1 != -1):
            idx2 = line.find(',', idx1)
            _FinalPrice = line[idx1 + len('FinalPrice":'):idx2]
            item['price'] = self._format_price(_CurrencyId, _FinalPrice)

    def _extract_list_price(self, sel, item):
        line = sel.response.body
        idx = line.find('ItemTotalLook')
        line = line[:idx]
        _CurrencyId = ''
        _ListPrice = ''
        _FinalPrice = ''
        idx1 = 0
        idx2 = 0
        idx1 = line.find('Prices":[{"CurrencyId":"')
        if(idx1 != -1):
            idx2 = line.find('",', idx1)
            _CurrencyId = line[idx1 + len('Prices":[{"CurrencyId":"'):idx2]
        idx_FinalPrice1 = line.find('FinalPrice":', idx2)
        idx_ListPrice1 = line.find('ListPrice":', idx2)
        if(idx_ListPrice1 != -1):
            idx2 = line.find(',', idx_ListPrice1)
            _ListPrice = line[idx1 + len('ListPrice":'):idx2]
        if(idx_FinalPrice1 != -1):
            idx2 = line.find(',', idx_FinalPrice1)
            _FinalPrice = line[idx1 + len('FinalPrice":'):idx2]
        if(_FinalPrice < _ListPrice):
            item['list_price'] = self._format_price(_CurrencyId, _ListPrice)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        line = sel.response.body
        idx = line.find('ItemTotalLook')
        line = line[:idx]
        _ShipCost = 0
        idx1 = line.find('ShipCost":')
        if(idx1 != -1):
            idx2 = line.find(',', idx1)
            _ShipCost = int(line[idx1 + len('ShipCost":'):idx2])
        if(_ShipCost == 0):
            item['is_free_shipping'] = True

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        pass

    def _extract_item_url(self, item_url):
        req = urllib2.Request(item_url)
        res_data = urllib2.urlopen(req)
        content = res_data.read()
        doc = HT.fromstring(content)
        _SeasonId = ''
        _CollectionId = ''
        _ItemId = ''
        _VendorColorId = ''
        _SeasonMemoCode = ''
        _GenderMemoCode = ''
        _SubLineMemoCode = ''
        _CategoryId = 0

        _SeasonId_xpath = '//input[@id="SeasonItemId"]/@value'
        data = doc.xpath(_SeasonId_xpath)
        if(len(data) != 0):
            _SeasonId = str(data[0])
        else:
            _SeasonId = ''
        _CollectionId_xpath = '//input[@id="ItemCode"]/@value'
        data = doc.xpath(_CollectionId_xpath)
        if(len(data) != 0):
            _CollectionId = str(data[0][:3])
        else:
            _CollectionId = ''
        _ItemId_xpath = '//input[@id="ItemCode"]/@value'
        data = doc.xpath(_ItemId_xpath)
        if(len(data) != 0):
            _ItemId = str(data[0][3:])
        else:
            _ItemId = ''
        _VendorColorId_xpath = '//input[@id="vendorColorId"]/@value'
        data = doc.xpath(_VendorColorId_xpath)
        if(len(data) != 0):
            _VendorColorId = str(data[0])
        else:
            _VendorColorId = ''
        _SeasonMemoCode_xpath = '//input[@id="SeasonMemoCode"]/@value'
        data = doc.xpath(_SeasonMemoCode_xpath)
        if(len(data) != 0):
            _SeasonMemoCode = str(data[0])
        else:
            _SeasonMemoCode = ''
        _GenderMemoCode_xpath = '//input[@id="GenderMemoCode"]/@value'
        data = doc.xpath(_GenderMemoCode_xpath)
        if(len(data) != 0):
            _GenderMemoCode = data[0]
        else:
            _GenderMemoCode = ''
        _SubLineMemoCode_xpath = '//input[@id="SubLineMemoCode"]/@value'
        data = doc.xpath(_SubLineMemoCode_xpath)
        if(len(data) != 0):
            _SubLineMemoCode = data[0]
        else:
            _SubLineMemoCode = ''
        _CategoryId_xpath = '//input[@id="CategoryID"]/@value'
        data = doc.xpath(_CategoryId_xpath)
        if(len(data) != 0):
            _CategoryId = data[0]
        else:
            _CategoryId = 0

        _target1 = ('http://www.luisaviaroma.com/ItemSrv.ashx?'
            'itemRequest={"SeasonId":"')
        _target2 = ('","Language":"","CountryId":"","SubLineMemoCode":"')
        _target3 = (',"ItemResponse":"itemResponse="'
            ',"MenuResponse":"menuResponse"'
            ',"SizeChart":false,"ItemTag":true,"NoContext":false}&time=')
        _time_stamp = str(time.time())
        new_item_url = (_target1 + _SeasonId + '","CollectionId":"'
            + _CollectionId + '","ItemId":"' + _ItemId + '","VendorColorId":"'
            + _VendorColorId + '","SeasonMemoCode":"' + _SeasonMemoCode
            + '","GenderMemoCode":"' + _GenderMemoCode + _target2
            + _SubLineMemoCode + '","CategoryId":' + str(_CategoryId)
            + _target3 + _time_stamp)
        return new_item_url

    def _simplify_item_url(
            self, sel, designerId, paletteColors, subcategory, item_urls):
        line = sel.response.body
        idx1 = line.find('"CatalogResults":[{')
        if(idx1 != -1):
            idx2 = line.find(';pricingResponse=')
            if(idx2 != -1):
                line = line[idx1 + len('"CatalogResults":[{'):idx2]
        _all_results = line.split('"DesignerLook"')
        _simplify_results = []
        if(len(designerId) == 0
           and len(paletteColors) == 0
           and len(subcategory) == 0):
            _simplify_results = _all_results
        else:
            for _line in _all_results:
                idx1 = _line.find('"SubCategory":[')
                if(idx1 != -1):
                    idx2 = _line.find(']', idx1)
                    _temp = _line[idx1 + len('"SubCategory":['):idx2]
                    idx = _temp.find('{"CategoryId":' + str(subcategory))
                    if(idx == -1):
                        continue
                if(_line.find('"Designer":{"DesignerId":"' + designerId) != -1):
                    idx1 = _line.find('"ColorDescription":"')
                    idx2 = _line.find('",', idx1 + len('"ColorDescription":"'))
                    _temp = _line[idx1 + len('"ColorDescription":"'):idx2]
                    if(_temp.find(paletteColors) != -1):
                        _simplify_results.append(_line)
        requests = self.get_requests(_simplify_results, item_urls)
        return requests

    def get_requests(self, _simplify_results, item_urls):
        requests = []
        for line in _simplify_results:
            idx1 = line.find('"UrlProductLang":"')
            if(idx1 != -1):
                while(True):
                    if(idx1 != -1):
                        idx2 = line.find('","', idx1)
                        item_url = line[idx1 + len('"UrlProductLang":"'):idx2]
                        new_item_url = (self._extract_item_url(item_url)
                            .replace(' ', '%20').replace('"', '%22')
                            .replace('[', '%5B').replace(']', '%5D')
                            .replace('{', '%7B').replace('}', '%7D'))
                        item_urls.append(new_item_url)
                        request = scrapy.Request(
                            new_item_url, callback=self.parse_item)
                        requests.append(request)
                        line = line[idx2:]
                        idx1 = line.find('"UrlProductLang":"')
                    else:
                        break
        return requests

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
