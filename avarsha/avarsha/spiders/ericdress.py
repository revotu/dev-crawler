# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline
import urllib2
import urllib
import re
import json

from w3lib.html import remove_tags
from avarsha_spider import AvarshaSpider
from scrapy.selector import Selector
from openpyxl import load_workbook

_spider_name = 'ericdress'

class EricdressSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["ericdress.com"]

    def __init__(self, *args, **kwargs):
        super(EricdressSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        
        base_url = ''
        items_xpath = '//dl[@class="garrery sepcial"]/dd/a/@href'

        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        
        dir = sel.response.url[sel.response.url.find('/list/') + len('/list/'):sel.response.url.find('/bestselling/')]
        dir = dir[:dir.rfind('-')]
        
        page = sel.response.url[sel.response.url.find('/bestselling/') + len('/bestselling/'):sel.response.url.rfind('/')]
        if len(page) > 0:
            page = int(page)
        else:
            page = 1
        pageSize = 96
        
        for index , path in enumerate(item_nodes):
            item_url = path + '?dir=' + dir + '&index=' + str((page - 1)*pageSize + index + 1)
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.ericdress.com'
        nexts_xpath = '//div[@class="g_r_t"]/a[@class="next"]/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="right_c"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        pass

    def _extract_sku(self, sel, item):
        url = sel.response.url[:sel.response.url.find('?')]
        item['sku'] = url[url.rfind('-') + len('-'): url.find('.htm')]

    def _extract_features(self, sel, item):
        description_xpath = '//div[@id="tab1"]/ul/li'
        data = sel.xpath(description_xpath).extract()
        if len(data) > 0 :
            data = [remove_tags(v).strip().replace('&nbsp;',' ').replace('&gt;','>').strip()  for v in data]
            data = filter(None,data)
            item['description'] = '<br>'.join(data)
            
    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        dir = 'ericdress'
        
        imgs_xpath = '//div[@id="thumbs"]/div[@class="list_images"]/ul/li/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = [ img + '#index=' + str(index + 1) + '&sku=' + item['sku'] + '&dir=' + dir for index ,img in enumerate(data)]

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        url = 'http://build.solr.ericdress.com:8080/getProductData?pids=%s' % (item['sku'])
        content = urllib2.urlopen(url).read()
        data = json.loads(content)
        item['price'] = data["Data"]["productDataList"][0]["Price"]
        item['stocks'] = data["Data"]["productDataList"][0]["SPUID"]
        
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
        dir = 'ericdress-reviews'
        review_url = 'http://www.ericdress.com/ajax/productreviewHandler.js?action=getProductReviewsPageInfo'
        query_args = {'spuId' : item['stocks'] , 'pageIndex' : '1' , 'pageSize' : '9999'}
        encoded_args  = urllib.urlencode(query_args)
        content = urllib2.urlopen(review_url , encoded_args).read()
        data = json.loads(content)
        if len(data) > 0:
            reviewData = json.loads(data['reviewData'])
            review_list = []
            if len(reviewData) > 0:
                for review in reviewData:
                    review_list.append({'username' : review['UserName'], 'content' : review['Content']})
                    if 'Images' in review:
                        for index , review_image in enumerate(review['Images']):
                            item['image_urls'].append(review_image + '#index=' + str(index + 1) + '&sku=' + item['sku'] + '&dir=' + dir)
        
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
