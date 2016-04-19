# -*- coding: utf-8 -*-
# author: tanyafeng

import re
import urllib2
import json

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'bebe'

class BebeSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["bebe.com"]

    def __init__(self, *args, **kwargs):
        super(BebeSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.bebe.com'
        items_xpath = '//*[@class="text-display"]//@href'

        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(self.convert_url(item_url))
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        return []

    def convert_url(self, url):
        return url.replace(' ' , '%20')

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="description-container"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Bebe'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'BEBE'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="item-no uppercase spaced"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@id="jsPDPTabContent"]/div/node()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        idx1 = sel.response.body.find('{"variantKeys"')
        idx2 = sel.response.body.find('class=\'variant COLOR_NAME\'')
        line = sel.response.body[idx1:idx2]
        imgset_pattern = re.compile('"RECOLORED_IMAGE":"(.*?)"')
        match = imgset_pattern.findall(line)
        for sub_str in set(match):
            fetch_img_url = ('http://www.bebe.com/catalog/get_image_set'
                             '.cmd?imageSet=%s_is') % sub_str
            content = urllib2.urlopen(fetch_img_url).read()
            dict_data = json.loads(content)
            match_urls = dict_data["images"]
            for match_url in match_urls:
                imgs.append(('http://s7d9.scene7.com/is/image/%s?$Detail2013$'
                    '&id=z1kqY1&wid=1400&hei=2000&fmt=jpg') % match_url)
        if len(imgs) != 0:
            item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        for line in sel.response.body.split('\n'):
            idx1 = line.find('{"variantKeys"')
            if idx1 != -1:
                idx2 = line.rfind('}')
                json_str = line[idx1:idx2 + 1]
                dict_data = json.loads(json_str)
                data = dict_data["attributeIndexes"][0]
                if len(data) != 0:
                    item['colors'] = data
                break

    def _extract_sizes(self, sel, item):
        sizes = []
        for line in sel.response.body.split('\n'):
            idx1 = line.find('{"variantKeys"')
            if idx1 != -1:
                idx2 = line.rfind('}')
                json_str = line[idx1:idx2 + 1]
                dict_data = json.loads(json_str)
                data = dict_data["attributeIndexes"][1]
                if len(data) != 0:
                    for sub_size in data:
                        sizes.append(''.join(sub_size.split('\\')))
                    item['sizes'] = sizes
                break

    def _extract_price(self, sel, item):
        price_xpath = '//*[@class="currentPrice"]/text()'
        sale_xpath = '//*[@class="salePrice"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) == 0:
            data = sel.xpath(sale_xpath).extract()
        if len(data) != 0:
            price_str = data[0].split('-')
            price_number = price_str[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//*[@class="basePrice"]/text()'
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

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        id_xpath = '//*[@id="description-container"]/div[@class="item-no uppercase spaced"]/text()'
        data = sel.xpath(id_xpath).extract()
        id = ''
        if len(data) != 0:
            id = data[0]
        review_url = 'http://bebe.ugc.bazaarvoice.com/6513redes/idnum/reviews.djs?format=embeddedhtml'
        review_url = review_url.replace('idnum', id)
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('BVRRTitle BVRRDisplayContentTitle')
        if indx1 == -1:
            item['review_count'] = 0
            return []
        indx2 = content.find('>', indx1) + len('>')
        indx3 = content.find('Review', indx2)
        data = content[indx2:indx3]
        data = data.replace('\\n', '')
        data = data.replace(" ", "")

        review_count = 0
        if len(data) != 0:
            review_count = int(data)
        item['review_count'] = review_count
        print "review_count", review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        indx1 = content.find('BVImgOrSprite')
        indx2 = content.find('alt=', indx1) + len('alt=')
        indx2 = content.find('"', indx2) + len('"')
        indx3 = content.find('/', indx2)
        data = content[indx2:indx3]

        if len(data) != 0:
            item['review_rating'] = float(data)
        review_num = 0;
        review_url0 = review_url
        pageidx = 0
        review_list = []
        while review_num < review_count:
            pageidx += 1
            pagenum = str(pageidx)
            review_url = review_url0 + '&page=' + pagenum + '&scrollToTop=true'
            request = urllib2.Request(review_url)
            response = urllib2.urlopen(request)
            content = []
            content = response.read()
            indx = content.find('BVSubmissionPopupContainer')
            while indx != -1:
                indx += len('BVSubmissionPopupContainer')
                indx1 = content.find('BVRRNumber BVRRRatingNumber', indx) + len('BVRRNumber BVRRRatingNumber')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                data = content[indx2:indx3]
                rating = float(data)
                indx1 = content.find('BVRRValue BVRRReviewDate', indx) + len('BVRRValue BVRRReviewDate')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                date = content[indx2:indx3]
                indx1 = content.find('BVRRNickname', indx) + len('BVRRNickname')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                name = content[indx2:indx3]
                indx1 = content.find('BVRRValue BVRRReviewTitle', indx) + len('BVRRValue BVRRReviewTitle')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('<', indx2)
                title = content[indx2:indx3]
                indx1 = content.find('span class=\\"BVRRReviewText\\"', indx) + len('span class=\\"BVRRReviewText\\"')
                indx2 = content.find('>', indx1) + len('>')
                indx3 = content.find('span', indx2)
                cont = content[indx2:indx3 - 2]
                review_list.append({'rating':rating,
                  'date':date,
                  'name':name,
                  'title':title,
                  'content':cont})
                indx = content.find('BVSubmissionPopupContainer', indx)
                review_num += 1
        item['review_list'] = review_list


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
