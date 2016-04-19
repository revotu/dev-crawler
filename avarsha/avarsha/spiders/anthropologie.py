# -*- coding: utf-8 -*-
# author: zhangliangliang

import scrapy.cmdline

import urllib2

import re

import json

from avarsha_spider import AvarshaSpider


_spider_name = 'anthropologie'

class AnthropologieSPider(AvarshaSpider):
    name = "anthropologie"
    allowed_domains = ["anthropologie.com"]

    def __init__(self, *args, **kwargs):
        super(AnthropologieSPider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx = url.find('#')
        if idx != -1:
            return url[:idx]
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = 'http://www.anthropologie.com'
        items_xpath = '//div[@class="item-description"]/a/@href'
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for node in item_nodes:
            item_url = base_url + node
            idx1 = item_url.find('#')
            if idx1 != -1:
                item_url = item_url[:idx1]
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        idx1 = sel.response.url.find('?')
        if idx1 == -1:
            return []
        base_url = sel.response.url[:idx1]
        nexts_xpath = '//a[@title="next"]/@href'

        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = base_url + path
            idx1 = list_url.find('#')
            if idx1 != -1:
                list_url = list_url[:idx1]
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Anthropologie'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//meta[@itemprop="brand"]/@content'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//meta[@itemprop="productId"]/@content'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//span[@itemprop="description"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line.strip()
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        data = re.search(re.compile(r'\d+'), sel.response.url)
        if data == None:
            return None
        api_link = 'http://www.anthropologie.com/api/v1/product/' + data.group()
        opener = urllib2.build_opener()
        opener.addheaders = [
                ('User-agent',
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 ' +
                '(KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36')
            ]
        response = opener.open(api_link)
        data = json.loads(response.read())
        try:
            if data.get('product', None) is not None and \
                data['product'].get('colors', None) is not None:
                all_colors = data['product']['colors']
                if len(all_colors) <= 0:
                    return None
                sizes = []
                imgs = []
                colors = []
                for line in all_colors[0]['sizes']:
                    sizes.append(line.get('displayName', None))
                for line in all_colors:
                    color = line.get('displayName', None)
                    pid = line.get('id', None)
                    view_codes = line.get('viewCode', None)
                    if pid is None or view_codes is None or color is None:
                        continue
                    colors.append(color)
                    for view_code in view_codes:
                        image_link = ('http://images.anthropologie.com/is/' + \
                            'image/Anthropologie/' + pid + '_' + view_code + \
                            '?$redesign-zoom-5x$')
                        imgs.append(image_link)
                item['colors'] = colors
                item['sizes'] = sizes
                item['image_urls'] = imgs
        except:
            return None

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).re('\d+\.?\d+')
        if len(data) != 0:
            price_number = data[0]
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

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        url = sel.response.url
        indx1 = url.find(".jsp")
        indx2 = url.rfind("/", 0, indx1)
        id = ''
        id = url[indx2 + 1:indx1]
        review_url = 'http://anthropologie.ugc.bazaarvoice.com/5310redes/idnum/reviews.djs?format=embeddedhtml'
        review_url = review_url.replace('idnum', id)
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('BVRRNumber BVRRBuyAgainTotal')
        if indx1 == -1:
            item['review_count'] = 0
            return []
        indx2 = content.find('>', indx1) + len('>')
        indx3 = content.find('<', indx2)
        data = content[indx2:indx3]
        review_count = 0
        if len(data) != 0:
            review_count = int(data)
        item['review_count'] = review_count
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
            review_url = review_url0 + '&page=' + pagenum + '&'
            request = urllib2.Request(review_url)
            response = urllib2.urlopen(request)
            content = []
            content = response.read()
            indx = content.find('BVSubmissionPopupContainer')
            while indx != -1:
                indx += len('BVSubmissionPopupContainer')
                indx1 = content.find('BVImgOrSprite', indx)
                indx2 = content.find('alt=', indx1) + len('alt=')
                indx2 = content.find('"', indx2) + len('"')
                indx3 = content.find('/', indx2)
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
                indx3 = content.find('<\/span>', indx2)
                contents = content[indx2:indx3]
                review_list.append({'rating':rating,
                  'date':date,
                  'name':name,
                  'title':title,
                  'content':contents})
                indx = content.find('BVSubmissionPopupContainer', indx)
                review_num += 1
        item['review_list'] = review_list


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
