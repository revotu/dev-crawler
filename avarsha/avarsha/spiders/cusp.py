# -*- coding: utf-8 -*-
# @author: donglongtu

import base64
import json
import re

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'cusp'

class CuspSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["cusp.com"]
    flag = 0
    ntt = ''
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(CuspSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def convert_url(self, url):
        idx = url.find('#')
        if idx != -1:
            if url.find('search') == -1:
                cat_index = url.find('cat')
                cat_end_index = url.find('_')
                cat = url[cat_index: cat_end_index]

                ref_reg = re.compile(r'&refinements=(.+?)&')
                data = ref_reg.findall(url)
                ref = data[0]

                parameters = ('{"GenericSearchReq":{"pageOffset":0,"pageSize":'
                    '"30","refinements":"%s","sort":"PCS_SORT","definitionPath"'
                    ':"/nm/commerce/pagedef/template/EndecaDriven'
                    'Home","userConstrainedResults":"true","advancedFilterReq'
                    'Items":{"StoreLocationFilterReq":[{"allStoresInput":"fals'
                    'e","onlineOnly":""}]},"categoryId":"%s","sortByFavorites"'
                    ':false,"isFeaturedSort":false,"prevSort":""}}' % (ref, cat))
                prefix_url = "http://www.cusp.com/category.service?data="
                tail_url = '&service=getCategoryGrid'
                url = (prefix_url + '$b64$' +
                    base64.urlsafe_b64encode(parameters) + tail_url)
                return url
            else:
                self.flag = 1

                ref_reg = re.compile(r'&refinements=(.+?)&')
                data = ref_reg.findall(url)
                ref = data[0]

                idx1 = url.find('Ntt=')
                idx2 = url.find('&_requestid')
                if idx2 != -1:
                    self.ntt = url[idx1 + len('Ntt='):idx2]
                else:
                    self.ntt = url[idx1 + len('Ntt='):]

                parameters = ('{"GenericSearchReq":{"pageOffset":0,"pageSize":'
                    '"30","refinements":"%s","sort":"","endecaDrivenSiloRefinem'
                    'ents":"0","definitionPath"'
                    ':"/nm/commerce/pagedef/etemplate/Search'
                    '","userConstrainedResults":"true","advancedFilterReq'
                    'Items":{"StoreLocationFilterReq":[{"allStoresInput":"fals'
                    'e","onlineOnly":""}]},"categoryId":"","ntt":"%s",'
                    '"sortByFavorites":false,"isFeaturedSort":false,"prevSort"'
                    ':""}}' % (ref, self.ntt))
                prefix_url = "http://www.cusp.com/category.service?data="
                tail_url = '&service=getFilteredEndecaResult'
                url = (prefix_url + '$b64$' +
                    base64.urlsafe_b64encode(parameters) + tail_url)
                return url
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.cusp.com'
        items_xpath = '//*[@class="prodImgLink"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        if sel.response.url.find('Ntt') != -1:
            self.flag = 1
            idx1 = sel.response.url.find('Ntt=')
            idx2 = sel.response.url.find('&_requestid')
            if idx2 != -1:
                self.ntt = sel.response.url[idx1 + len('Ntt='):idx2]
            else:
                self.ntt = sel.response.url[idx1 + len('Ntt='):]
        idx = sel.response.url.find('category.service')
        ref = ''
        if idx == -1:
            cat_index = sel.response.url.find('cat')
            cat_end_index = sel.response.url.find('_')
            cat = sel.response.url[cat_index: cat_end_index]

            max_page_xpath = '//div[@id="epaging"]/div[last()-1]/text()'
            max_page = sel.xpath(max_page_xpath).extract()
            if len(max_page) != 0:
                max_page = int(max_page[0])
            else:
                max_page = 1
        else :
            max_page_reg = re.compile(r'"totalPages":(.+?),')
            max_page = max_page_reg.findall(sel.response.body)[0]
            max_page = int(max_page)

            base64_url_reg = re.compile(r'\$b64\$(.+?)&service')
            base64_url = base64_url_reg.findall(sel.response.url)
            utf8_url = base64.urlsafe_b64decode(base64_url[0])
            utf8_url = json.loads(utf8_url)

            cat = utf8_url['GenericSearchReq']['categoryId']
            ref = utf8_url['GenericSearchReq']['refinements']

        if max_page != 1:
            requests = []
            for page in range(max_page - 1):
                prefix_url = "http://www.cusp.com/category.service?data="

                if self.flag == 0:
                    parameters = ('{"GenericSearchReq":{"pageOffset":%s'
                        ',"pageSize":"30","refinements":"%s","sort":"PCS_SORT",'
                        '"definitionPath":"/nm/commerce/pagedef/template/'
                        'EndecaDrivenHome","userConstrainedResults":"true",'
                        '"advancedFilterReqItems":{"Store'
                        'LocationFilterReq":[{"allStoresInput":"false",'
                        '"onlineOnly":""}]},"categoryId":"%s'
                        '","sortByFavorites":false,"isFeaturedSort":false,'
                        '"prevSort":""}}' % (str(page + 1), ref, cat))
                    tail_url = '&service=getCategoryGrid'
                else:
                    parameters = ('{"GenericSearchReq":{"pageOffset":%s'
                        ',"pageSize":"30","refinements":"%s","sort":"",'
                        '"endecaDrivenSiloRefinements":"0","definitionPath":"'
                        '/nm/commerce/pagedef/etemplate/Search","userConstrain'
                        'edResults":"true","advancedFil'
                        'terReqItems":{"StoreLocationFilterReq":[{"allStores'
                        'Input":"false","onlineOnly":""}]},"categoryId":"",'
                        '"ntt":"%s","sortByFavorites":false,"isFeaturedSort":'
                        'false,"prevSort":""}}' % (str(page + 1), ref, self.ntt))
                    tail_url = '&service=getFilteredEndecaResult'

                url = (prefix_url + '$b64$' +
                    base64.urlsafe_b64encode(parameters) + tail_url)

                list_urls.append(url)
                requests.append(scrapy.Request(url, callback=self.parse))
            return requests
        else :
            return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//title/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Cusp'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@itemprop="brand"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@name="itemId"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="cutline short hideShort"]/div/'
            'div[@itemprop="description"]/h2')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = ('//img[@class="alt-shot"]/@data-zoom-url'
            ' | //*[@itemprop="image"]/@data-zoom-url')
        data = sel.xpath(imgs_xpath).extract()
        data = list(set(data))
        if len(data) != 0:
            for img in data:
                imgs.append(img)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//div[@class="lineItemInfo"]/div[@class="adornment'
            'PriceElement"]/div[@class="price pos2"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()[len('$'):]
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
