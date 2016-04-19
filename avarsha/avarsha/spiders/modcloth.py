# -*- coding: utf-8 -*-
# author: zhangliangliang
import re
import scrapy.cmdline
import urllib2
from avarsha_spider import AvarshaSpider
import re
from scrapy.selector import Selector


_spider_name = 'modcloth'

class ModclothSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["modcloth.com"]

    def __init__(self, *args, **kwargs):
        super(ModclothSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.modcloth.com'
        items_xpath = '//div[@class="product-info"]/p[1]/a[1]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.modcloth.com'
        nexts_xpath = '//a[@class="next_page"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@id="pdp-product-name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Modcloth'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//h2[@itemprop="brand"]/a[@itemprop="name"]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        for line in sel.response.body.split('\n'):
            idx1 = line.find('product_id = \'')
            if idx1 != -1:
                idx2 = line.find('\',', idx1)
                if idx2 != -1:
                    item['sku'] = line[idx1 + len('product_id = \''):idx2]
                    break


    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@itemprop="description"]/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = data[0].strip() + data[1].strip()
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        for line in sel.response.body.split('\n'):
            idx1 = line.find('hi_res_url : \'')
            if idx1 != -1:
                idx2 = line.find('\',', idx1)
                img_url = line[idx1 + len('hi_res_url : \''):idx2].strip()
                imgs.append(img_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//table[@class="measurements-data"]/thead/tr//th/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data[1:]

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@class="product_price_sale"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            list_price_number = data[0][len('$'):].strip()
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
        review_count_xpath = '//a[@class="reviews-count"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if len(data) == 0:
            return []
        indx = data[0].find('Reviews')
        data = data[0][:indx]

        if 'No' in data:
            item['review_count'] = 0
            return []
        review_count = int(data)
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        review_rating_xpath = '//div[@class="review-stars"]/div/@class'
        data = sel.xpath(review_rating_xpath).extract()
        data = data[0].replace('is-', '')
        data = data.replace('-stars', '')
        item['review_rating'] = float(data)
        content = sel.response.body
        indx1 = content.find('product_id = \'')
        if indx1 == -1:
            return []
        indx1 += len('product_id = \'')
        indx2 = content.find('\'', indx1)
        id = content[indx1:indx2]
        base_url = 'http://www.modcloth.com/storefront/reviews/view_more/idnum?place='
        base_url = base_url.replace('idnum', id)
        pagenum = 0
        content = ''
        review_list = []
        while True:
            review_url = base_url + str(pagenum)
            pagenum += 10
            request = urllib2.Request(review_url)
            response = urllib2.urlopen(request)
            content = response.read()
            indx1 = content.find('"review_count":')
            if indx1 == -1:
                break
            indx1 += len('"review_count":')
            indx2 = content.find(',', indx1)
            page_count = int(content[indx1:indx2])
            if page_count == 0:
                break
            indx = content.find('review_wrapper user-review')
            while indx != -1:
                indx += len('review_wrapper user-review')
                indx1 = content.find('review-stars', indx)
                indx1 = content.find('is-', indx1) + len('is-')
                indx2 = content.find('-stars', indx1)
                rating = float(content[indx1:indx2])
                indx1 = content.find('review-left-date', indx)
                indx1 = content.find('>', indx1) + len('>')
                indx2 = content.find('&nbsp', indx1)
                date = content[indx1:indx2]
                date = self.clearblank(date)
                indx1 = content.find('review_info_name', indx)
                indx1 = content.find('>', indx1) + len('>')
                indx2 = content.find('<', indx1)
                name = content[indx1:indx2]
                name = self.clearblank(name)
                indx1 = content.find('review_comment', indx)
                indx1 = content.find('>', indx1) + len('>')
                indx2 = content.find('<', indx1)
                cont = content[indx1:indx2]
                cont = self.clearblank(cont)
                review_list.append({'rating':rating,
                  'date':date,
                  'name':name,
                  'title':'',
                  'content':cont})
                indx = content.find('review_wrapper user-review', indx)
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
