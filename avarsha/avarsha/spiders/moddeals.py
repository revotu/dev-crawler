# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

from avarsha_spider import AvarshaSpider
import urllib2
from scrapy.selector import Selector
_spider_name = 'moddeals'

class ModdealsSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["moddeals.com"]

    def __init__(self, *args, **kwargs):
        super(ModdealsSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.moddeals.com'
        items_xpath = '//ul[@id="categories"]//li/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.moddeals.com'
        nexts_xpath = '//a[@class="paging_next paging_text_active"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Moddeals'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'ModDeals'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@id="prod-detail-sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][len('Item: '):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@itemprop="description"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            des = ''
            for line in data:
                des += line
            item['description'] = des

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        images_xpath = '//ul[@id="product_image_list"]//li/a/@href'
        imgs = sel.xpath(images_xpath).extract()
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//div[@id="prod-detail-sku"]/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            idx = data[0].rfind('-')
            data[0] = data[0][idx + 1:]
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//ul[@id="product_size_box"]//li/text()'
        size_list = sel.xpath(size_list_xpath).extract()
        if len(size_list) != 0:
            item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD ', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="previous_price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            idx1 = data[0].find('$')
            price_num = data[0][idx1 + 1:].strip()
            item['list_price'] = self._format_price('USD', price_num)

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
        review_count_xpath = '//div[@id="product_main"]/div[@id="product_info"]/form' + \
        '/div[@class="star_container"]/span[@itemprop="reviewcount"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if(len(data) == 0):
            item['review_count'] = 0
            return []
        review_count = int(data[0])
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        review_rating_xpath = ('//div[@id="product_main"]/div[@id="product_info"]/form' +
        '/div[@class="star_container"]/span[@itemprop="ratingValue"]/text()')
        data = sel.xpath(review_rating_xpath).extract()
        item['review_rating'] = float(data[0])
        url = sel.response.url
        reviews_url = url.replace('http://www.moddeals.com/p/', 'http://www.moddeals.com/reviews/')
        print reviews_url
        request = urllib2.Request(reviews_url)
        response = urllib2.urlopen(request)
        content = response.read()
        sel = Selector(text=content)
        ratings_xpath = ('//div[@id="product_reviews"]/div[@class="review_item"]/' +
        'div[@class="review_content"]//div[@class="star_on"]/@style')
        dates_xpath = '//div[@id="product_reviews"]/div[@class="review_item"]/div[@class="review_content"]/i/text()'
        names_xpath = '//div[@id="product_reviews"]/div[@class="review_item"]/div[@class="review_member"]/img/@alt'
        titles_xpath = '//div[@id="product_reviews"]/div[@class="review_item"]/div[@class="review_content"]/span[1]/text()'
        conts_xpath = '//div[@id="product_reviews"]/div[@class="review_item"]/div[@class="review_content"]'
        ratings = sel.xpath(ratings_xpath).extract()
        dates = sel.xpath(dates_xpath).extract()
        names = sel.xpath(names_xpath).extract()
        titles = sel.xpath(titles_xpath).extract()
        conts = sel.xpath(conts_xpath).extract()
        print conts[0]
        valid_count = min(len(ratings), len(dates), len(names), len(titles), len(conts))
        review_list = []
        print review_count
        print ratings
        for j in xrange(review_count):
            indx1 = ratings[j].find('width:') + len('width:')
            indx2 = ratings[j].find('%', indx1)
            ratings[j] = float(ratings[j][indx1:indx2]) / 100.0 * 5.0
            indx1 = conts[j].find('</i>') + len('</i>')
            indx2 = conts[j].find('style', indx1)
            print indx1, indx2
            conts[j] = conts[j][indx1:indx2]
            conts[j] = conts[j].replace('<br>', '')
            conts[j] = conts[j].replace('<br', '')
            conts[j] = conts[j].replace('\r\n', '')
            conts[j] = self.clearblank(conts[j])
            review_list.append({'rating':ratings[j],
                              'date':dates[j],
                              'name':names[j],
                              'title':titles[j],
                              'content':conts[j]})
        item['review_list'] = review_list
    def clearblank(self, stri):
        stri = stri.replace('\\n', '')
        left = 0
        right = len(stri) - 1
        while stri[left] == ' ':
            left += 1
            if left == len(stri):
                break
        while stri[right] == ' ':
            right -= 1
            if right <= left:
                break
        return stri[left:right + 1]


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
