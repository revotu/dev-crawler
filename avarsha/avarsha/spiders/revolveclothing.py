# -*- coding: utf-8 -*-
# @author: donglongtu

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'revolveclothing'

class RevolveclothingSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["revolveclothing.com"]

    def __init__(self, *args, **kwargs):
        super(RevolveclothingSpider, self).__init__(*args, **kwargs)

    def _find_nexts_from_list_page(self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            if list_url.find(' ') != -1:
                list_url = list_url.replace(' ', '%20')
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.revolveclothing.com'
        items_xpath = '//*[@class="plp_text_link"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.revolveclothing.com'
        nexts_xpath = '//*[@class="result_pages"]/ul/li/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@property="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Revolveclothing'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@property="brand"]/a/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_reg = re.compile(r'currentCode = \'(.+?)\'')
        sku = sku_reg.findall(sel.response.body)
        if len(sku) != 0:
            item['sku'] = sku[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="pdp_product_info_panel active"]/ul'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//*[@class="pdp_main_img_thumbs"]/ul/li/a/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for img in data:
                imgs.append(img.replace('dt', 'z'))
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//*[@class="price_box"]/span[@class="price"]/text()'
            ' | //span[@class="discount_price"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="original_price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0].strip()[len('$'):]
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

    def _extract_max_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        review_count_xpath = '//div[@class="reviews_total"]/div[@class="pdp_review_title"]/span/text()'
        data = sel.xpath(review_count_xpath).extract()
        if(len(data) == 0):
            item['review_count'] = 0
            return []
        data[0] = data[0].replace('REVIEWS', '')
        review_count = int(data[0])
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        review_rating_xpath = '//div[@class="pdp_review_overall"]/div[@class="reviewer_star_number"]/div[@class="pdp_review_title"]/text()'
        data = sel.xpath(review_rating_xpath).extract()
        item['review_rating'] = float(data[0].replace('(', '').replace(')', ''))
        ratings_xpath = '//div[@typeof="Review"]//span[@property="ratingValue"]/text()'
        names_xpath = '//div[@typeof="Review"]//span[@property="author"]/text()'
        titles_xpath = '//div[@typeof="Review"]//span[@itemprop="summary"]/text()'
        contents_xpath = '//div[@typeof="Review"]//span[@property="reviewBody"]'
        ratings = sel.xpath(ratings_xpath).extract()
        names = sel.xpath(names_xpath).extract()
        titles = sel.xpath(titles_xpath).extract()
        contents = sel.xpath(contents_xpath).extract()
        review_list = []
        for indx in range(len(ratings)):
            ratings[indx] = float(ratings[indx])
            indx1 = contents[indx].find('reviewBody') + len('reviewBody')
            indx2 = contents[indx].find('>', indx1) + len('>')
            indx3 = contents[indx].find('</span', indx2)
            review_list.append({'rating':ratings[indx],
              'date':'',
              'name':names[indx],
              'title':titles[indx],
              'content':contents[indx][indx2:indx3]})
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()