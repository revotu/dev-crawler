# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re
import urllib2
import scrapy.cmdline
from avarsha_spider import AvarshaSpider
_spider_name = 'johnlewis'

class JohnlewisSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["johnlewis.com"]

    def __init__(self, *args, **kwargs):
        super(JohnlewisSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://us.johnlewis.com'
        items_xpath = '//div[@class="qv-image-holder"]/a/@href'
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            idx = item_url.find('?')
            if(idx != -1):
                item_url = item_url[:idx] + (
                    item_url[idx:].replace(' ', '%20').replace('^', '%5E')
                    .replace('/', '%2F').replace('"', '%22')
                    .replace('[', '%5B').replace(']', '%5D')
                    .replace('{', '%7B').replace('}', '%7D'))
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        base_url = 'http://us.johnlewis.com'
        nexts_xpath = '//li[@class="next"]/a/@href'
        nexts = sel.xpath(nexts_xpath).extract()
        list_url = ''
        if(len(nexts) != 0):
            list_url = nexts[0]
        if(list_url == '#'):
            return requests
        if list_url.find(base_url) == -1:
            list_url = base_url + list_url
        list_urls.append(list_url)
        request = scrapy.Request(list_url, callback=self.parse)
        requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@id="prod-title"]/span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Johnlewis'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = (
            '//div[@itemprop="brand"]/span[@itemprop="name"]/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]
        else:
            item['brand_name'] = 'Johnlewis'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@id="prod-product-code"]/p/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = str(data[0])

    def _extract_features(self, sel, item):
        _features = {}
        _key = ''
        _value = ''
        features_xpath = '//div[@class="tab-content"]//dl'
        data = sel.xpath(features_xpath).extract()
        if len(data) != 0:
            for line in data:
                idx1 = line.find('<dt>')
                if(idx1 != -1):
                    idx2 = line.find('<', idx1 + len('<dt>'))
                    _key = line[idx1:idx2]
                    data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]')
                    _key = data_re.sub('', _key)
                    line = line[idx2:]
                idx1 = line.find('<dd>')
                if(idx1 != -1):
                    idx2 = line.find('</dd>')
                    _value = line[idx1:idx2]
                    data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]')
                    _value = data_re.sub('', _value)
                _features[_key] = _value
            item['features'] = _features

    def _extract_description(self, sel, item):
        description_xpath = ('//span[@itemprop="description"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        image_urls_xpath = '//ul[@class="thumbnails"]//img/@src'
        data = sel.xpath(image_urls_xpath).extract()
        image_urls2_xpath = '//img[@itemprop="image"]/@src'
        data2 = sel.xpath(image_urls2_xpath).extract()
        if len(data) != 0:
            for line in data:
                if(line.find('http:') == -1):
                    line = 'http:' + line
                _image_url = line.replace('$prod_thmb2$', '$prod_exlrg$')
                imgs.append(_image_url)
        if(len(imgs) == 0):
            if (len(data2) != 0):
                line = data2[0]
                if(line.find('http:') == -1):
                    line = 'http:' + line
                _image_url = line.replace('$prod_main$', '$prod_lrg$')
                imgs.append(_image_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@class="now-price"]/text()')
        price2_xpath = '//strong[@class="simpleNowPrice"]/text()'
        price3_xpath = '//p[@class="price"]/strong/text()'
        data = sel.xpath(price_xpath).extract()
        data2 = sel.xpath(price2_xpath).extract()
        data3 = sel.xpath(price3_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]')
            new_data = data_re.sub('', data[0])
            item['price'] = self._format_price('USD', new_data)
        elif len(data2) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +|["$]|Now')
            new_data = data_re.sub('', data2[0])
            item['price'] = self._format_price('USD', new_data)
        elif len(data3) != 0:
            line = data3[0]
            idx1 = line.find('-')
            if(idx1 != -1):
                line = line[:idx1]
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+| +|["$]|Now')
            new_data = data_re.sub('', line)
            item['price'] = self._format_price('USD', new_data)

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
        product_id_xpath = '//div[@id="catId"]/text()'
        data = sel.xpath(product_id_xpath).extract()
        id = ''
        if len(data) == 0:
            return []
        else:
            id = data[0]
        review_url = 'http://johnlewis.ugc.bazaarvoice.com/7051redes-en_gb/idnum/reviews.djs?format=embeddedhtml'
        review_url = review_url.replace('idnum', id)
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('BVRRCount BVRRNonZeroCount')
        if indx1 == -1:
            item['review_count'] = 0
            return []
        indx1 = content.find('BVRRNumber', indx1)
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
            tp = 0
            if indx == -1:
                indx = content.find('BVRRRatingsOnlySummaryTitle')
                tp = 1
                if indx == -1:
                    review_num += 1
            while indx != -1:
                rating = 0
                date = ''
                name = ''
                cont = ''
                title = ''
                if tp == 0:
                    indx += len('BVSubmissionPopupContainer')
                else:
                    indx += len('BVRRRatingsOnlySummaryTitle')
                indx1 = content.find('BVRRNumber BVRRRatingNumber', indx)
                if indx1 != -1:
                    indx1 += len('BVRRNumber BVRRRatingNumber')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    data = content[indx2:indx3]
                    rating = float(data)
                indx1 = content.find('BVRRValue BVRRReviewDate', indx)
                if indx1 != -1:
                    indx1 += len('BVRRValue BVRRReviewDate')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    date = content[indx2:indx3]
                indx1 = content.find('BVRRNickname', indx)
                if indx1 != -1:
                    indx1 += len('BVRRNickname')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    name = content[indx2:indx3]
                indx1 = content.find('BVRRValue BVRRReviewTitle', indx)
                if indx1 != -1:
                    indx1 += len('BVRRValue BVRRReviewTitle')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('<', indx2)
                    title = content[indx2:indx3]
                indx1 = content.find('span class=\\"BVRRReviewText\\"', indx)
                if indx1 != -1:
                    indx1 += len('span class=\\"BVRRReviewText\\"')
                    indx2 = content.find('>', indx1) + len('>')
                    indx3 = content.find('span', indx2)
                    cont = content[indx2:indx3 - 3]
                review_list.append({'rating':rating,
                  'date':date,
                  'name':name,
                  'title':title,
                  'content':cont})
                indx = content.find('BVSubmissionPopupContainer', indx)
                if indx == -1:
                    indx = content.find('BVRRRatingsOnlySummaryTitle', indx)
                review_num += 1
        item['review_list'] = review_list



def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
