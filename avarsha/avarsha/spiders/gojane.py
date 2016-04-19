# -*- coding: utf-8 -*-
# @author: wanghaiyi

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = "gojane"

class GojaneSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["gojane.com", "search.gojane.com"]

    def __init__(self, *args, **kwargs):
        super(GojaneSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.gojane.com/'
        items_xpath = ('//noscript//a/@href | //div[@class="nxt_image_wrapper"]'
            '/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.gojane.com'
        base_url2 = 'search.gojane.com'
        nexts_xpath = ('//span[@class="page-number"]/@data-number-link | //a'
        '[@class="nxt-pages-next"]/@href')
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url2) == -1:
                list_url = base_url + path
            list_url = list_url.replace(' ', '')
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[contains(@class,"current")]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Gojane'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Gojane'

    def _extract_sku(self, sel, item):
        data = sel.response.url[sel.response.url.rfind('/') + 1:]
        if len(data) != 0:
            item['sku'] = data.strip('.html')

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//meta[@name="Description"]/@content'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//a[@class="fancybox"]/@rel | '
            '//a[@class="fancybox feat"]/@rel')
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_list = []
        color_xpath = '//a/@data-sizes'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                cmp = data[i]
                cmp = cmp[:cmp.rfind('-')]
                color_list.append(cmp[cmp.rfind('-') + 1:])
        if len(color_list) != 0:
            item['colors'] = color_list

    def _extract_sizes(self, sel, item):
        size_list = []
        size_list_xpath = '//a/@data-sizes'
        data = sel.xpath(size_list_xpath).extract()
        tmp_char = ''
        if len(data) != 0:
            for i in range(len(data)):
                while data[i].rfind(';') != -1:
                    tmp_char = data[i][data[i].rfind('|') + 1:data[i].rfind(';')]
                    if tmp_char not in size_list :
                        size_list.append(tmp_char)
                        data[i] = data[i][:data[i].rfind('|')]
                    else:
                        data[i] = data[i][:data[i].rfind('|')]
        if len(size_list) != 0:
            item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$', ''))


    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@id="retail-price"]/s/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            item['list_price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        pass

    def _extract_review_count(self, sel, item):
        review_count = 0
        sel = Selector(sel.response)
        review_count_xpath = '//span[@itemprop="reviewCount"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if len(data) != 0:
            review_count = int(data[0])
        if review_count != 0:
            item['review_count'] = review_count

    def _extract_review_rating(self, sel, item):
        review_count = 0
        review_rating = 0
        review_sum = 0.0
        sel = Selector(sel.response)
        review_count_xpath = '//span[@itemprop="reviewCount"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if len(data) != 0:
            review_count = int(data[0])
            rating_xpath = '//div[@class="prReviewerRating"]/text()'
            ratings = sel.xpath(rating_xpath).extract()
            for i in range(0 , review_count):
                ratings[i] = float(ratings[i].rstrip(' Stars'))
                review_sum = review_sum + ratings[i]
            review_rating = float(review_sum) / float(review_count)
        if review_count != 0:
            item['review_rating'] = review_rating
            item['max_review_rating'] = 5

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        review_count = 0
        review_rating = 0
        review_sum = 0.0
        review_list = []
        sel = Selector(sel.response)
        review_count_xpath = '//span[@itemprop="reviewCount"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if len(data) != 0:
            review_count = int(data[0])
            review_name_xpath = '//div[contains(@class,"prReviewerName")]/text()'
            data = sel.xpath(review_name_xpath).extract()
            if len(data) != 0:
                names = data
            rating_xpath = '//div[@class="prReviewerRating"]/text()'
            ratings = sel.xpath(rating_xpath).extract()
            for i in range(0 , review_count):
                ratings[i] = float(ratings[i].rstrip(' Stars'))
                review_sum = review_sum + ratings[i]
            titles_xpath = '//div[@class="prTitle"]/text()'
            titles = sel.xpath(titles_xpath).extract()
            review_rating = float(review_sum) / float(review_count)
            review_content_xpath = '//div[@class="prBody"]/text()'
            review_date_xpath = '//div[@class="prReviewDate"]/text()'
            dates = sel.xpath(review_date_xpath).extract()
            data = sel.xpath(review_content_xpath).extract()
            for i in range(len(data)):
                data[i] = data[i].strip()
            if len(data) != 0:
                review_contents = data
            for j in range(len(names)):
                review_list.append({'rating':ratings[j],
                    'name':names[j], 'date':dates[j],
                    'title':titles[j], 'content':review_contents[j]})
        if len(review_list) != 0:
            item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
