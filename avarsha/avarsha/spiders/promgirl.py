# -*- coding: utf-8 -*-
# author: yangxiao

import re

import scrapy.cmdline
from scrapy import log
from scrapy.selector import Selector

from avarsha.items import ProductItem
from avarsha_spider import AvarshaSpider


_spider_name = 'promgirl'

class PromgirlSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["promgirl.com"]

    def __init__(self, *args, **kwargs):
        super(PromgirlSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.promgirl.com'
        items_xpath = '//h4[@class="book"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        if 'find' in self.start_urls[0]:
            base_url = 'http://www.promgirl.com/shop/find'
        else:
            base_url = 'http://www.promgirl.com'
        nexts_xpath = ('//span[@class="page-links"]/label[@for="nt"]/a/@href |'
            '//label[@class="pagination"]/a/@href')

        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def parse_item(self, response):
        self.log('Parse item link: %s' % response.url, log.DEBUG)

        sel = Selector(response)
        item = ProductItem()

        # each spider overrides the following methods
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
        self._extract_colors(sel, item)
        self._extract_sizes(sel, item)
        self._extract_stocks(sel, item)

        # extract list_price first, then extract price
        self._extract_list_price(sel, item)
        self._extract_price(sel, item)

        self._extract_low_price(sel, item)
        self._extract_high_price(sel, item)
        self._extract_is_free_shipping(sel, item)
        self._extract_review_count(sel, item)
        self._extract_review_rating(sel, item)
        self._extract_best_review_rating(sel, item)
        self._extract_review_list(sel, item)

        # auto filled methods, don't need to override them
        self._save_product_id(sel, item)
        self._record_crawl_datetime(item)
        self._save_product_collections(sel, item)

        return item

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//header[@class="pdp-header clearfix"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'promgirl'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'promgirl'

    def _extract_sku(self, sel, item):
        sku_xpath = ('//meta[@itemprop="sku"]/@content')
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_title_xpath = '//div[@class="content"]/div/*'
        description_content_xpath = '//table[@class="table pdp"]/*'
        data_title = sel.xpath(description_title_xpath).extract()
        data_content = sel.xpath(description_content_xpath).extract()
        data = []
        data.append(data_title[0])
        data += data_content
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_list_xpath = ('//ul[@class="main-thumbs col-sm-2 col-lg-2"]'
            '/li/a/@href')
        data = sel.xpath(imgs_list_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = ('//select[@title="color"]/option/text()')
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data[1:]

    def _extract_sizes(self, sel, item):
        size_xpath = '//select[@title="size"]/option/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data[1:]

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        if item.get('list_price') != None:
            price_xpath = '//p[@class="price"]/span/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = re.search('\$(.*)$', data[1]).group(1)
                item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = '//p[@class="price"]/span/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price_number = re.search('\$(.*)$', data[0]).group(1)
                item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//p[@class="price"]/span[@class="suggested"]\
            /text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = re.search('\$(.*)$', data[0]).group(1)
            item['list_price'] = self._format_price('USD', price_number)

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
        vote_count_xpath = '//meta[@itemprop="ratingCount"]/@content'
        data = sel.xpath(vote_count_xpath).extract()
        if(len(data) == 0):
            item['review_count'] = 0
            return []
        vote_count = int(data[0])
        if vote_count == 0:
            return []
        item['max_review_rating'] = 5
        review_rating_xpath = '//div[@class="aggregate-rating"]/span[@itemprop="ratingValue"]/text()'
        data = sel.xpath(review_rating_xpath).extract()
        item['review_rating'] = float(data[0])
        review_count_xpath = '//span[@itemprop="reviewCount"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if(len(data) == 0):
            item['review_count'] = 0
            return []
        review_count = int(data[0])
        item['review_count'] = review_count
        if review_count == 0:
            return []
        ratings_xpath = ('//div[@class="existing-reviews"]/div[@id="more-reviews"]//ul[@class="list"]' +
                       '//div[@itemprop="review"]//span[@itemprop="ratingValue"]/text()')
        ratings = sel.xpath(ratings_xpath).extract()
        if len(ratings) == 0:
            ratings_xpath = ('//div[@class="existing-reviews"]/ul[@class="list"]' +
                             '//div[@itemprop="review"]//span[@itemprop="ratingValue"]/text()')
            dates_xpath = ('//div[@class="existing-reviews"]/ul[@class="list"]' +
                             '//div[@itemprop="review"]//meta[@itemprop="datePublished"]/@content')
            names_xpath = ('//div[@class="existing-reviews"]/ul[@class="list"]' +
                             '//div[@itemprop="review"]//span[@class="reviewer"]/text()')
            titles_xpath = ('//div[@class="existing-reviews"]/ul[@class="list"]' +
                             '//div[@itemprop="review"]/div[@class="reviews-title text-muted"]/text()')
            contents_xpath = ('//div[@class="existing-reviews"]/ul[@class="list"]' +
                             '//div[@itemprop="review"]/div[@class="description"]')
        else:
            dates_xpath = ('//div[@class="existing-reviews"]/div[@id="more-reviews"]//ul[@class="list"]' +
                             '//div[@itemprop="review"]//meta[@itemprop="datePublished"]/@content')
            names_xpath = ('//div[@class="existing-reviews"]/div[@id="more-reviews"]//ul[@class="list"]' +
                             '//div[@itemprop="review"]//span[@class="reviewer"]/text()')
            titles_xpath = ('//div[@class="existing-reviews"]/div[@id="more-reviews"]//ul[@class="list"]' +
                             '//div[@itemprop="review"]/div[@class="reviews-title text-muted"]/text()')
            contents_xpath = ('//div[@class="existing-reviews"]/div[@id="more-reviews"]//ul[@class="list"]' +
                             '//div[@itemprop="review"]/div[@class="description"]')
        ratings = sel.xpath(ratings_xpath).extract()
        dates = sel.xpath(dates_xpath).extract()
        names = sel.xpath(names_xpath).extract()
        titles = sel.xpath(titles_xpath).extract()
        contents = sel.xpath(contents_xpath).extract()
        review_list = []
        for indx in range(len(ratings)):
            ratings[indx] = float(ratings[indx])
            indx1 = contents[indx].find('itemprop') + len('itemprop')
            indx2 = contents[indx].find('>', indx1) + len('>')
            indx3 = contents[indx].find('</div', indx2)
            contents[indx] = contents[indx][indx2:indx3]
            review_list.append({'rating':ratings[indx],
              'date':dates[indx],
              'name':names[indx],
              'title':titles[indx],
              'content':contents[indx]})
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
