# -*- coding: utf-8 -*-
# @author: wanghaiyi

import urllib2

import scrapy.cmdline

import math

from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = "shopbop"

class ShopbopSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["shopbop.com"]

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/53'
        '7.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}

    def __init__(self, *args, **kwargs):
        super(ShopbopSpider, self).__init__(*args, **kwargs)

    def make_requests_from_url(self, url):
        return scrapy.Request(url, dont_filter=True, headers=self.headers)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.shopbop.com'
        items_xpath = '//div[@class="border-container"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.shopbop.com'
        nexts_xpath = '//span[@class="page-number"]/@data-number-link'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)


    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@class="row product-title"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Shopbop'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = ('//h1[@class="brand-heading"]/'
            'a[@itemprop="brand"]/text()')
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//span[@itemprop="sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0]


    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@itemprop="description"]'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        for line in sel.response.body.split('\n'):
            idx1 = line.find('\"zoom\": ')
            if idx1 != -1:
                idx2 = line.find('\"' , idx1 + len('\"zoom\": '))
                img_url = line[idx2 + 1:-1].strip()
                imgs.append(unicode(img_url))
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        color_xpath = '//div[@id="swatches"]/img/@title'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//div[@id="sizes"]/span[@class="size hover"]/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//div[contains(@class,"priceBlock")]/text() | //'
            'span[@class="salePrice"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                if data[i].find('$') != -1:
                    data[i] = data[i].strip()
                    if data[i].find('US') == -1:
                        item['price'] = self._format_price('USD', data[i].replace('$', ''))
                    else:
                        item['price'] = self._format_price('USD', data[i].replace('US$', ''))

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="originalRetailPrice"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            data[0] = data[0].strip()
            if data[0].find('US') == -1:
                item['list_price'] = self._format_price('USD', data[0].replace('$', ''))
            else:
                item['list_price'] = self._format_price('USD', data[0].replace('US$', ''))

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        free_shipping_xpath = '//div[@class="content row"]/p/b/text()'
        data = sel.xpath(free_shipping_xpath).extract()
        if len(data) != 0:
            for i in range(len(data)):
                if data[i].strip() == 'Free Shipping Worldwide:':
                    item['is_free_shipping'] = True
                    break
                else:
                    item['is_free_shipping'] = False

    def _extract_review_count(self, sel, item):
        pass

    def _extract_review_rating(self, sel, item):
        pass

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        count_xpath = '//meta[@itemprop="reviewCount"]/@content'
        data = sel.xpath(count_xpath).extract()
        review_count = 0
        if len(data) == 0:
            item['review_count'] = 0
            return []
        review_count = int(data[0])
        item['review_count'] = review_count
        if review_count == 0:
            return []
        rating_xpath = '//meta[@itemprop="ratingValue"]/@content'
        data = sel.xpath(rating_xpath).extract()
        review_rating = 5.0
        if len(data) != 0:
            review_rating = float(data[0])
        item['review_rating'] = review_rating
        item['max_review_rating'] = 5
        url = sel.response.url
        indx = url.find('&os=false')
        url_head = url[:indx]
        review_list = []
        for i in xrange(int(math.ceil(review_count / 10.0))):
            content = ''
            reviews_url = url_head + '&baseIndex=%d&os=false' % (10 * i)
            request = urllib2.Request(reviews_url)
            response = urllib2.urlopen(request)
            content = response.read()
            sel = Selector(text=content)
            review_rating_xpath = ('//div[@class="reviews-contianer"]' +
                                   '//span[@class="review-rating"]/img[@class="rating-stars"]/@src')
            review_name_xpath = '//div[@class="reviews-contianer"]//div[@class="name"]/text()'
            review_title_xpath = '//div[@class="reviews-contianer"]//span[@class="review-title"]/text()'
            review_content_xpath = '//div[@class="reviews-contianer"]//div[@class="review-text"]'
            ratings = sel.xpath(review_rating_xpath).extract()
            names = sel.xpath(review_name_xpath).extract()
            titles = sel.xpath(review_title_xpath).extract()
            review_contents = sel.xpath(review_content_xpath).extract()
            for j in range(len(ratings)):
                indx1 = ratings[j].find('stars-orange-') + len('stars-orange-')
                indx2 = ratings[j].find('_', indx1)
                ratings[j] = float(ratings[j][indx1:indx2])
                indx1 = review_contents[j].find('review-text') + len('review-text')
                indx2 = review_contents[j].find('>', indx1) + len('>')
                indx3 = review_contents[j].find('</div', indx2)
                review_contents[j] = review_contents[j][indx2:indx3]
                review_contents[j] = self.clearblank(review_contents[j])
                titles[j] = self.clearblank(titles[j])
                names[j] = self.clearblank(names[j])
                review_list.append({'rating':ratings[j],
                                  'date':'',
                                  'name':names[j],
                                  'title':titles[j],
                                  'content':review_contents[j]})
        item['review_list'] = review_list

    def clearblank(self, stri):
        while '\n' in stri:
            stri = stri.replace('\n', '')
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
