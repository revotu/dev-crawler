# -*- coding: utf-8 -*-
# author: zhangliangliang

import urllib2

import math

import scrapy.cmdline

from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'nordstrom'

class NordstromSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["shop.nordstrom.com"]

    def __init__(self, *args, **kwargs):
        super(NordstromSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://shop.nordstrom.com'
        items_xpath = '//*[@class="title"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        parent_url = sel.response.url
        idx = parent_url.find('?')
        base_url = parent_url[0:idx]
        nexts_xpath = '//*[@class="page-number "]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Nordstrom'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//section[@id="brand-title"]/h2/a/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@class="item-number-wrapper"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][len('Item #'):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_part1_xpath = '//*[@class="accordion-content"]/p'
        data1 = sel.xpath(description_part1_xpath).extract()
        if len(data1) != 0:
            item['description'] = data1[0]
        description_part2_xpath = '//*[@class="accordion-content"]/ul'
        data2 = sel.xpath(description_part2_xpath).extract()
        if len(data2) != 0:
            part2 = data2[0].replace(' class="style-features"', '')
            part2 = part2.replace('\n\t\t\t\t\t\t', '')
            part2 = part2.replace('\n\t\t\t\t', '')
            if item.get('description'):
                item['description'] += part2
            else:
                item['description'] = part2

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//li[@class="image-thumb"]/button/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = []
            for img in data:
                item['image_urls'].append(img.replace('/Mini/', '/Zoom/'))

    def _extract_colors(self, sel, item):
        color_list_xpath = '//*[@id="color-selector"]/option/text()'
        data = sel.xpath(color_list_xpath).extract()
        if len(data) != 0:
            item['colors'] = data[1:]

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//*[@id="size-buttons"]//li/button/@value'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@class="item-price heading-2"]/span/text()'
        price1_xpath = '//td[@class="item-price"]/span[@class="sale-price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_num = data[0][len('$'):]
            item['price'] = self._format_price('USD', price_num)
        else:
            data = sel.xpath(price1_xpath).extract()
            if len(data) != 0:
                price_num = data[0][len('Now: $'):]
                item['price'] = self._format_price('USD', price_num)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//td[@class="item-price"]/span[@class="regular-price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0][len('Was: $'):].strip()
            item['list_price'] = self._format_price('USD', list_price_number)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        free_shipping_xpath = '//*[@class="item-free-shipping"]/text()'
        data = sel.xpath(free_shipping_xpath).extract()
        if len(data) != 0 and data[0].strip() == 'Free Shipping':
            item['is_free_shipping'] = True

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_max_review_rating(self, sel, item):
        pass

    def __remove_escape(self, content):
        content = content.replace('\\"', '"')
        content = content.replace('\\n', '')
        content = content.replace('\\/', '/')
        return content

    def _extract_review_list(self, sel, item):
        for lines in sel.xpath('//script/text()').extract():
            for line in lines.split('\n'):
                idx1 = line.find('"bazaarvoiceStyleId":"')
                if idx1 != -1:
                    idx2 = line.find('",', idx1)
                    style_id = line[idx1 + len('"bazaarvoiceStyleId":"'):idx2]
                    break
        first_review_url = ('http://nordstrom.ugc.bazaarvoice.com/4094redes/'
                '%s/reviews.djs?format=embeddedhtml' % style_id)

        content = urllib2.urlopen(first_review_url).read()
        content = self.__remove_escape(content)
        sel = Selector(text = content)

        review_count = 0
        review_list = []
        review_count_xpath = '//*[@itemprop="reviewCount"]/@content'
        data = sel.xpath(review_count_xpath).extract()
        if len(data) != 0:
            review_list = []
            review_count = int(data[0])
            review_rating_xpath = ('//span[@class='
                    '"BVRRNumber BVRRRatingNumber"]/text()')
            review_rating = float(sel.xpath(review_rating_xpath).extract()[0])
            for i in xrange(1, int(math.ceil(review_count / 4.0 + 1))):
                review_url = ('http://nordstrom.ugc.bazaarvoice.com/4094redes/'
                        '%s/reviews.djs?format=embeddedhtml&page='
                        '%d&scrollToTop=true' % (style_id, i))
                review_resquest = urllib2.Request(review_url)
                review_response = urllib2.urlopen(review_resquest)
                content = review_response.read()
                content = self.__remove_escape(content)

                sel = Selector(text = content)

                review_name_xpath = '//span[@class="BVRRNickname"]/text()'
                names = sel.xpath(review_name_xpath).extract()

                review_date_xpath = (
                    '//span[@class="BVRRValue BVRRReviewDate"]/text()')
                dates = sel.xpath(review_date_xpath).extract()

                rating_xpath = ('//div[@itemprop="reviewRating"]/'
                        'span[@class="BVRRNumber BVRRRatingNumber"]/text()')
                ratings = sel.xpath(rating_xpath).extract()

                titles_xpath = (
                    '//span[@class="BVRRValue BVRRReviewTitle"]')
                titles = []
                for p_title in sel.xpath(titles_xpath):
                    title = p_title.xpath('text()').extract()
                    if len(title) == 0:
                        titles.append('')
                    else:
                        titles.append(title[0])

                review_content_xpath = (
                    '//div[@class="BVRRReviewTextContainer"]//span/text()')
                review_contents = sel.xpath(review_content_xpath).extract()

                for j in range(len(names)):
                    review_list.append({'rating':int(ratings[j]),
                        'date':dates[j],
                        'name':names[j],
                        'title':titles[j],
                        'content':review_contents[j]})

            if review_rating != 0:
                item['max_review_rating'] = 5
                item['review_rating'] = review_rating
            if review_count != 0:
                item['review_count'] = review_count
            if len(review_list) != 0:
                item['review_list'] = review_list


def main():
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
