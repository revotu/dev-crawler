# -*- coding: utf-8 -*-
# author: yangxiao

import re
import urllib2

import scrapy.cmdline
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'kohls'

class KohlsSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ['kohls.com', 'kohls.ugc.bazaarvoice.com']
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(KohlsSpider, self).__init__(*args, **kwargs)

        setting = get_project_settings()
        setting.set('User-Agent', self.user_agent)

    def convert_url(self, url):
        if '#' in url:
            return url[:url.index('#')]
        if ' ' in url:
            return url.replace(' ', '%20')
        else:
            return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.kohls.com'
        items_xpath = '//*[@id="product-matrix"]/li/a/@href'

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

        base_url = 'http://www.kohls.com'
        nexts_xpath = '//div[@class="view-indicator"]//a/@href'

        # don't need to change this line
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            list_urls.append(self.convert_url(list_url))
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//div[@class="pdp_title"]/h1/text() |'
            '//h1[@class="title productTitleName"]/text() |'
            '//h1[@class="title productTitleName"]/strong/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'kohls'

    def _extract_brand_name(self, sel, item):
        try:
            item['brand_name'] = re.search('(.*)\xae|(.*)\\u2122', \
                item['title']).group(1)
        except AttributeError:
            item['brand_name'] = 'kohls'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="column_content_container"]/input/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]
        else:
            item['sku'] = re.search('var productID = \'(.+?)\'', \
                sel.response.body).group(1)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="product_Lpanel"]'
            '//div[@class="Bdescription"]/*')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = ''.join(data)

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_list_xpath = '//div[@id="leftCarousel"]//li//img/@src'
        data = sel.xpath(imgs_list_xpath).extract()
        if len(data) != 0:
            for index in range(len(data)):
                data[index] = data[index].replace('wid=50&hei=50&', \
                    'wid=882&hei=882&')
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = ('//div[@class="price-varitions"]'
            '/div[@class="swatch-container-new"]/div/a/@id')
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_xpath = ('//div[@class="size-holder"]/div[@id="size-waist"]'
            '/div/a/@id')
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[@class="sale"]/span[@class="price_ammount"]'
            '/text()')
        data = sel.xpath(price_xpath).extract()
        try:
            price_number = re.search('\s*(\$.*)\s*', data[0]).group(1)\
                .replace('$', '')
        except:
            price_xpath = ('//div[@class="original original-reg"]/text()')
            data = sel.xpath(price_xpath).extract()
            try:
                price_number = re.search('\s*(\$.*)\s*', data[-1]).group(1).replace('$', '')
            except:
                price_xpath = ('//div[@class="sale"]/text()')
                data = sel.xpath(price_xpath).extract()
                try:
                    price_number = re.search('\s*(\$.*)\s*', data[-2]).group(1).replace('$', '')
                except:
                    price_xpath = ('//div[@class="original"]/text()')
                    data = sel.xpath(price_xpath).extract()
                    try:
                        price_number = re.search('\s*(\$.*)\s*', data[1]).group(1).replace('$', '')
                    except:
                        pass
        if '-' in price_number:
            price_number = \
                price_number[:price_number.index('-') - 1]
        item['price'] = self._format_price("USD", price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="original"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_number = re.search('\s*(\$.*)\s*', data[1]).group(1)\
                .replace('$', '')
            if '-' in price_number:
                price_number = price_number[:price_number.index('-') - 1]
            if self._format_price("USD", price_number) != item['price']:
                item['list_price'] = self._format_price("USD", price_number)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        pass

    def _extract_review_count(self, sel, item):
        review_count = 0
        first_review_url = ('http://kohls.ugc.bazaarvoice.com/9025/%s'
            '/reviews.djs?format=embeddedhtml' % item['sku'])
        content = urllib2.urlopen(first_review_url).read()
        content = self.__remove_escape(content)
        sel_reviews = Selector(text=content)

        review_count_xpath = '//meta[@itemprop="reviewCount"]/@content'
        data = sel_reviews.xpath(review_count_xpath).extract()
        if len(data) != 0:
            review_count = int(data[0])
        item['review_count'] = review_count

    def _extract_review_rating(self, sel, item):
        review_rating = 0.0
        first_review_url = ('http://kohls.ugc.bazaarvoice.com/9025/%s'
            '/reviews.djs?format=embeddedhtml' % item['sku'])
        content = urllib2.urlopen(first_review_url).read()
        content = self.__remove_escape(content)
        sel_reviews = Selector(text=content)
        review_rating_xpath = '//span[@class="BVRRNumber BVRRRatingNumber"]\
            /text()'
        data = sel_reviews.xpath(review_rating_xpath).extract()
        if len(data) != 0:
            review_rating = float(data[0])
        item['review_rating'] = review_rating

    def _extract_best_review_rating(self, sel, item):
        item['max_review_rating'] = 5.00

    def _extract_review_list(self, sel, item):
        review_list = []
        if item['review_count'] > 0:
            review_list = []
            for i in range(1, item['review_count'] / 4 + 2):
                review_url = ('http://kohls.ugc.bazaarvoice.com/9025/'
                    '%s/reviews.djs?format=embeddedhtml&page='
                    '%d&scrollToTop=true' % (item['sku'], i))
                content = urllib2.urlopen(review_url).read()
                content = self.__remove_escape(content)

                sel_reviews = Selector(text=content)

                review_name_xpath = '//span[@class="BVRRNickname"]/text()'
                names = sel_reviews.xpath(review_name_xpath).extract()

                review_date_xpath = '//span[@class="BVRRValue BVRRReviewDate"]\
                    /text()'
                dates = sel_reviews.xpath(review_date_xpath).extract()

                rating_xpath = ('//span[@class="BVRRNumber BVRRRatingNumber"]\
                    /text()')
                ratings = sel_reviews.xpath(rating_xpath).extract()

                titles_xpath = '//span[@class="BVRRValue BVRRReviewTitle"]'
                titles = sel_reviews.xpath(titles_xpath).extract()
                for i in range(len(titles)):
                    titles[i] = re.search('>(.*)<', titles[i]).group(1)

                review_content_xpath = ('//div[@class="BVRRReviewTextContainer"]'
                    '//span[@class="BVRRReviewText"]/text() |'
                    '//div[@class="BVRRReviewTextContainer"]//'
                    'div[@class="BVRRNoReviewText"]/text()')
                review_contents = sel_reviews.xpath(review_content_xpath)\
                    .extract()

                for j in range(len(names)):
                    review_list.append({'rating':float(ratings[j]),
                        'date':dates[j],
                        'name':names[j],
                        'title':titles[j],
                        'content':review_contents[j]})

        item['review_list'] = review_list

    def __remove_escape(self, content):
        content = content.replace('\\\"', '"')
        content = content.replace('\\n', '')
        content = content.replace('\\/', '/')
        return content

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
