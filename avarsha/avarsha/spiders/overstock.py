# -*- coding: utf-8 -*-
# @author: zhangliangliang

import urllib2

import scrapy.cmdline

import math

from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'overstock'

class OverstockSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["overstock.com"]

    def __init__(self, *args, **kwargs):
        super(OverstockSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        result_count_xpath = '//span[@class="results-count"]/span/text()'
        data = sel.xpath(result_count_xpath).extract()
        if len(data) != 0:
            result_count = int(data[0].replace(',', ''))
            content = ''
            for i in range(result_count / 25 + 1):
                index = 25 * i + 1
                url = sel.response.url + \
                            '?index=%d&count=25&infinite=true' % index
                body = ''
                try:
                    body = urllib2.urlopen(url).read()
                except:
                    continue
                content += self.__remove_escape(body)
            sel = Selector(text = content)
            base_url = ''
            items_xpath = '//*[@class="pro-thumb"]/@href'
            # don't need to change this line
            return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        return []

    def __remove_escape(self, content):
        content = content.replace('\\\"' , '"')
        content = content.replace('\\n' , '')
        content = content.replace('\\/' , '/')
        return content

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@itemprop="name"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Overstock'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'OverStock'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="item-number"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            sku_num = data[0].strip()[6:]
            item['sku'] = sku_num

    def _extract_features(self, sel, item):
        feature_xpath = ('//table[@class="table table-dotted '
            'table-extended table-header translation-table"]'
            '/tbody//tr//td/text()')
        data = sel.xpath(feature_xpath).extract()
        content = {}
        if len(data) != 0:
            idx = 2
            while idx < len(data):
                key = data[idx].replace('\t', '').replace('\r', '')\
                    .replace('\n', '').strip()
                value = data[idx + 1].replace('\t', '').replace('\r', '')\
                    .replace('\n', '').strip()
                content[key] = value
                idx += 2
        item['features'] = content

    def _extract_description(self, sel, item):
        description_xpath1 = '//div[@class="description toggle-content"]/b'
        description_xpath2 = '//div[@class="description toggle-content"]/text()'
        description_xpath3 = '//div[@class="description toggle-content"]/ul'
        data1 = sel.xpath(description_xpath1).extract()
        data2 = sel.xpath(description_xpath2).extract()
        data3 = sel.xpath(description_xpath3).extract()
        content = ''
        if len(data1) != 0:
            for line in data1:
                content += line.strip()
        if len(data2) != 0:
            for line in data2:
                content += line.strip()
        if len(data3) != 0:
            for line in data3:
                content += line.strip()
        item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//div[@class="thumb-section"]/'
                      'div[@class="thumbs featured cf"]'
                      '/div[@class="thumb-frame"]/ul//li/@data-max-img')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = ('//table[@class="table table-dotted table-extended '
            'table-header translation-table"]/tbody/tr[1]/td[2]/text()')
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            color_list = []
            for line in data:
                for Tcolor in line.split('\t'):
                    if len(Tcolor) != 0:
                        color = Tcolor.replace('\n', '').replace('\r', '')
                        if len(color) != 0:
                            color_list.append(color)
            item['colors'] = color_list

    def _extract_sizes(self, sel, item):
        sizes_xpath = '//select[@class="options-dropdown"]//option/text()'
        data = sel.xpath(sizes_xpath).extract()
        size_list = []
        if len(data) != 0:
            for line in data:
                idx1 = line.find('-')
                idx2 = line.rfind('-')
                idx3 = line.find(',')
                if idx1 != -1 and idx2 != -1 and idx1 < idx2:
                    size_list.append(line[idx1 + 1:idx2].strip())
                elif idx3 != -1 and idx2 != -1 and idx3 < idx2:
                    size_list.append(line[idx3 + 1:idx2].strip())
        item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            if data[0].find('$') != -1:
                item['price'] = data[0].replace('$', 'USD ')
            else:
                item['price'] = data[0].strip()

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
        count_xpath = '//span[@class="count"]/text()'
        data = sel.xpath(count_xpath).extract()
        review_count = 0
        if len(data) != 0:
            idx1 = data[0].find('R')
            if idx1 != -1:
                if len(data[0][:idx1].strip()) != 0:
                    review_count = int(data[0][:idx1].strip())
        item['review_count'] = review_count

        if review_count == 0:
            return []

        rating_xpath = '//div[@itemprop="ratingValue"]/text()'
        data = sel.xpath(rating_xpath).extract()
        review_rating = 5.0
        if len(data) >= 2:
            rating_num = data[1].replace('\t', '').replace('\n', '').strip()
            if len(rating_num) != 0:
                review_rating = float(rating_num)
        item['review_rating'] = review_rating

        item['max_review_rating'] = 5

        idx1 = sel.response.url.rfind('/')
        if idx1 == -1:
            return []
        content = ''
        for i in xrange(int(math.ceil(review_count / 20.0))):
            reviews_url = sel.response.url[:idx1] + \
                '/customer-reviews.html?rpage=%d&rsort=4' % i
            request = urllib2.Request(reviews_url)
            response = urllib2.urlopen(request)
            content += response.read()
        sel = Selector(text = content)
        review_rating_xpath = '//div[contains(@id, "reviewInner")]/img/@src'
        review_date_xpath = ('//div[contains(@id, "reviewInner")]'
                                '/div[@class="marginTop10"]/text()')
        review_name_xpath = ('//div[contains(@id, "reviewInner")]'
                             '/div/div/a/text()')
        review_title_xpath = ('//div[contains(@id, "reviewInner")]'
                '/div[1]/a[contains(@id, "reviewTitle")]/text()')
        review_content_xpath = '//div[contains(@id, "reviewText")]/p/text()'

        ratings = []
        data = sel.xpath(review_rating_xpath).extract()
        if len(data) != 0:
            for line in data:
                idx1 = line.rfind('stars')
                if idx1 != -1:
                    tg = idx1 + len('stars')
                    ratings.append(int(line[tg:tg + 1]))
        dates = []
        data = sel.xpath(review_date_xpath).extract()
        if len(data) != 0:
            idx1 = 3
            while idx1 < len(data):
                date_num = data[idx1].replace('\n', '').strip()
                if len(date_num) != -1:
                    idx2 = len(date_num) - 1
                    while idx2 >= 0:
                        if date_num[idx2] >= 'A' and date_num[idx2] <= 'Z':
                            dates.append(date_num[idx2:])
                            break
                        idx2 -= 1
                idx1 += 4
        names = []
        data = sel.xpath(review_name_xpath).extract()
        if len(data) != 0:
            for line in data:
                names.append(line.strip())
        titles = []
        data = sel.xpath(review_title_xpath).extract()
        if len(data) != 0:
            for line in data:
                titles.append(line.strip())
        review_contents = []
        data = sel.xpath(review_content_xpath).extract()
        if len(data) != 0:
            for line in data:
                review_contents.append(line.strip())
        review_list = []
        for j in xrange(review_count):
            review_list.append({'rating':ratings[j],
                              'date':dates[j],
                              'name':names[j],
                              'title':titles[j],
                              'content':review_contents[j]})
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
