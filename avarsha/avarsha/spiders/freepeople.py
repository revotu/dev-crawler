# -*- coding: utf-8 -*-
# @author: donglongtu

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'freepeople'

class FreepeopleSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["freepeople.com"]

    def __init__(self, *args, **kwargs):
        super(FreepeopleSpider, self).__init__(*args, **kwargs)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            if list_url.find(' ') != -1:
                list_url = list_url.replace(' ', '%20')
            idx1 = list_url.find('SEARCHCLICKID')
            idx2 = list_url.find('startResult')
            if idx1 != -1 and idx2 != -1:
                prefix = list_url[:idx1]
                list_url = prefix + list_url[idx2:]
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//*[@class="thumbnail--large thumbnail"]/div/div/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.freepeople.com'
        nexts_xpath = '//*[@title="Next"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//*[@itemprop="name"]/text() | '
            '//div[@class="metadata"]/p/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Freepeople'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Freepeople'

    def _extract_sku(self, sel, item):
        sku_xpath = ('//span[@data-integration="productDetail-styleNumber"]'
            '/text()')
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = ('//*[@class="product-translation-content"]/'
            'div[@class="content"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//*[@class="alternates clearfix"]/ul/li/a/@href'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for img in data:
                imgs.append(img.replace('detail-item', 'zoom-superxl'))
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_list_xpath = ('//ul[@class="clearfix"]/li/a/img/@alt | //*[@data'
            '-integration="productDetail-colorAlias"]/text()'
            ' | //div[@data-option-name="Color"]/dl/dd/text()')
        data = sel.xpath(color_list_xpath).extract()
        if len(data) != 0:
            item['colors'] = []
            for color in data:
                if color.strip() != '' and color.strip() not in item['colors']:
                    item['colors'].append(color.strip())

    def _extract_sizes(self, sel, item):
        size_list_xpath = ('//li[@class="instock"]/a/span/text() | '
            '//li[@class="backordered"]/a/span/text() | '
            '//div[@data-option-name="Size"]/dl/dd/text()')
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = []
            for size in data:
                if ((size.strip() != '') and (size.strip() not in item['sizes'])
                        and (size.strip() != 'Select a size')):
                    item['sizes'].append(size.strip())

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath_1 = '//*[@itemprop="price"]/span[@class="dollars"]/text()'
        data_1 = sel.xpath(price_xpath_1).extract()
        price_xpath_2 = '//*[@itemprop="price"]/sup[@class="cents"]/text()'
        data_2 = sel.xpath(price_xpath_2).extract()
        if len(data_1) != 0 and len(data_2) != 0:
            price_number = data_1[0].strip() + data_2[0].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath_1 = ('//*[@class="price price-original"]/span'
            '[@class="dollars"]/text()')
        data_1 = sel.xpath(list_price_xpath_1).extract()
        list_price_xpath_2 = ('//*[@class="price price-original"]/sup'
            '[@class="cents"]/text()')
        data_2 = sel.xpath(list_price_xpath_2).extract()
        if len(data_1) != 0 and len(data_2) != 0:
            list_price_number = data_1[0].strip() + data_2[0].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        pass

    def _extract_reviews(self, sel, item):
        review_count = 0
        review_rating = 0
        review_list = []

        style_id_xpath = ('//*[@data-integration="productDetail-styleNumber"]'
            '/text()')
        data = sel.xpath(style_id_xpath).extract()
        if len(data) != 0:
            style_id = data[0].strip()

        first_review_url = ('http://freepeople.ugc.bazaarvoice.com/3393-en_us/'
            '%s/reviews.djs?format=embeddedhtml&scrollToTop'
            '=true' % style_id)

        content = urllib2.urlopen(first_review_url).read()
        content = self._remove_escape(content)
        sel = Selector(text=content)

        review_count_xpath = ('//*[@class="BVRRCount BVRRNonZeroCount"]/'
            'span/text()')
        data = sel.xpath(review_count_xpath).extract()
        if len(data) != 0:
            review_list = []
            review_count = int(data[0])
            review_rating_xpath = ('//*[@itemprop="aggregateRating"]/span'
                    '[@itemprop="ratingValue"]/text()')
            review_rating = float(sel.xpath(review_rating_xpath).extract()[0])

            for i in range(1, review_count / 8 + 2):
                review_url = ('http://freepeople.ugc.bazaarvoice.com/3393-en_'
                    'us/%s/reviews.djs?format=embeddedhtml&page='
                    '%d&scrollToTop=true' % (style_id, i))
                try :
                    content = urllib2.urlopen(review_url).read()
                except :
                    continue
                content = self._remove_escape(content)
                sel = Selector(text=content)

                review_name_xpath = '//span[@class="BVRRNickname"]/text()'
                names = sel.xpath(review_name_xpath).extract()

                review_date_xpath = ('//span[@class="BVRRValue BVRRReview'
                    'Date"]/text()')
                dates = sel.xpath(review_date_xpath).extract()

                rating_xpath = ('//div[@itemprop="reviewRating"]/'
                    'span[@class="BVRRNumber BVRRRatingNumber"]/text()')
                ratings = sel.xpath(rating_xpath).extract()

                titles_xpath = ('//span[@class = "BVRRValue BVRRReviewTitle"]'
                    '/text()')
                titles = sel.xpath(titles_xpath).extract()

                review_content_xpath = ('//span[@class="BVRRReviewText"]')
                review_conts = sel.xpath(review_content_xpath).extract()
                for i in range(len(names)):
                    review_conts[i] = review_conts[i][29:-7].replace('<br>', '')

                for j in range(len(names)):
                    review_list.append({'rating':float(ratings[j]),
                        'date':dates[j],
                        'name':names[j],
                        'title':titles[j],
                        'content':review_conts[j]})
                item['max_review_rating'] = 5
                item['review_count'] = review_count
                item['review_rating'] = review_rating
                item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
