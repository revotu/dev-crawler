# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re
import urllib2
import json
import scrapy.cmdline
import time
from time import *
from avarsha_spider import AvarshaSpider
from datetime import date


_spider_name = 'pacsun'

class PacsunSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["pacsun.com"]

    def __init__(self, *args, **kwargs):
        super(PacsunSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx1 = url.find('#')
        idx2 = url.rfind('&q=')
        parmt = ''
        if(idx1 != -1):
            url = url[:idx1] + url[idx1 + len('#'):] + '&format=ajax'
        elif(idx2 != -1):
            parmt = url[idx2 + len('&q='):]
            parmt = (parmt
                .replace('&', '%26').replace(' ', '%20')
                .replace('/', '%2F').replace('[]', '%5B%5D'))
            url = url[:idx2 + len('&q=')] + parmt
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@class="name"]/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="pagination"]/ul//li/a/@href'

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="productname"]//*/text()'
        data = sel.xpath(title_xpath).extract()
        _title = []
        if len(data) != 0:
            for _data in data:
                data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
                _title.append(data_re.sub('', _data))
            item['title'] = ' '.join(_title)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Pacsun'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@class="brandLogo"]//img/@title'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'amp;')
            item['brand_name'] = data_re.sub('', data[0])

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="itemNo productid"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            data_re = re.compile(r'[#]|(?:Sku)+| +')
            item['sku'] = str(data_re.sub('', data[0]))

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description1_xpath = '//div[@class="description"]/p'
        data1 = sel.xpath(description1_xpath).extract()
        description2_xpath = '//div[@class="description"]/ul'
        data2 = sel.xpath(description2_xpath).extract()
        _description = ''
        if len(data1) != 0:
            _description = ''.join([_description, data1[0]])
        if len(data2) != 0:
            _description = ''.join([_description, data2[0]])
        item['description'] = _description.strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        image_url = ''
        imgs_url_xpath = '//div[@class="productthumbnails"]//img/@src'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        if len(data_imgs) != 0:
            for image_url in data_imgs:
                idx1 = image_url.rfind('dw-product-thumb$');
                image_url = ''.join([image_url[:idx1], \
                    "dw-product-detail$&scl=1"])
                imgs.append(image_url)
            idx1 = image_url.find('_');
            idx2 = image_url.rfind('_');
            image_url = '_00'.join([image_url[:idx1], image_url[idx2:]])
            imgs.append(image_url)
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="promoprice"]/text()'
        data1 = sel.xpath(price_xpath).extract()
        price_xpath = '//div[@class="standardprice"]/text()'
        data2 = sel.xpath(price_xpath).extract()
        if len(data1) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|[:$]|Promotion')
            price = data_re.sub('', data1[len(data1) - 1])
            item['price'] = self._format_price('USD', str(price))
        elif len(data2) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|[$]')
            price = data_re.sub('', data2[len(data2) - 1])
            item['price'] = self._format_price('USD', str(price))

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="standardprice greyprice"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|[:$]|Original')
            list_price = data_re.sub('', data[len(data) - 1])
            item['list_price'] = self._format_price('USD', str(list_price))

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
        content = sel.response.body
        indx1 = content.find('streamID: \'')
        if indx1 == -1:
            return []
        indx1 += len('streamID: \'')
        indx2 = content.find('\'', indx1)
        id = content[indx1:indx2]
        review_url = ('http://comments.us1.gigya.com/comments.getComments?' +
                      'categoryID=products&streamID=idnum&includeSettings=true' +
                      '&threaded=false&includeStreamInfo=true&includeUserOptions=true' +
                      '&lang=en&ctag=comments_v1&APIKey=3_YZllzrvNQz9voPj8OsPial06kw1aV10p' +
                      'FrzfGEMxbIYNxLc7JyoeklNBeoYMCW1k&source=showCommentsUI&sourceData=%7B%22' +
                      'categoryID%22%3A%22products%22%2C%22streamID%22%3A%22idnum%22%7D&sdk=js_5.7.3' +
                      '&format=jsonp&callback=gigya._.apiAdapters.web.callback')
        review_url = review_url.replace('idnum', id)
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('{')
        indx2 = content.rfind('}')
        content = content[indx1:indx2 + 1]

        review_dict = json.loads(content)
        if ('commentCount' in review_dict.keys()):
            review_count = int(review_dict['commentCount'])
        else:
            item['review_count'] = -1
            return []
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        item['review_rating'] = float(review_dict['streamInfo']['avgRatings']['_overall'])
        review_results = review_dict['comments']
        review_list = []
        for idx in range(len(review_results)):
            date = review_results[idx]['timestamp']
            date = float(date) / 1000.0
            date = self.secs2str(date)
            name = review_results[idx]['sender']['name']
            title = review_results[idx]['commentTitle']
            contents = review_results[idx]['commentText']
            review_list.append({'rating':None,
              'date':date,
              'name':name,
              'title':title,
              'content':contents})
        item['review_list'] = review_list
    def secs2str(self, secs):
        return strftime("%Y-%m-%d %H:%M:%S", localtime(secs))
def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
