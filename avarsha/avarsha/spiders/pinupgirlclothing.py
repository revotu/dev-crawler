# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'pinupgirlclothing'

class PinupgirlclothingSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["pinupgirlclothing.com"]

    def __init__(self, *args, **kwargs):
        super(PinupgirlclothingSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.pinupgirlclothing.com'
        items_xpath = '//*[@class="products-grid"]/li/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.pinupgirlclothing.com'
        nexts_xpath = '//*[@class="next i-next"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@class="product-name"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Pinupgirlclothing'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Pinupgirlclothing'

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@name="product"]/@value'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desc_xpath = '//*[@class="tab-content"]/div[@class="std"]'
        data = sel.xpath(desc_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        imgs_xpath = '//*[@id="productGallery"]/li/a/@data-zoom-image'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            for img in data:
                imgs.append(img.strip())
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = ('//*[@class="regular-price"]/span[@class="price"]/text()'
            ' | //*[@class="special-price"]/span[@class="price"]'
            '/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@class="old-price"]/span[@class'
            '="price"]/text()')
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0 :
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

    def _extract_best_review_rating(self, sel, item):
        pass

    def _extract_review_list(self, sel, item):
        review_count_xpath = '//h5[@class="review-count"]/span/text()'
        data = sel.xpath(review_count_xpath).extract()
        if(len(data) == 0):
            item['review_count'] = 0
            return []
        data[0] = data[0].replace('Reviews', '')
        review_count = int(data[0])
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        review_rating_xpath = '//div[@class="ratings"]/div[@class="rating-box"]/div[@class="rating"]/@style'
        data = sel.xpath(review_rating_xpath).extract()
        indx1 = data[0].find('width:') + len('width:')
        indx2 = data[0].find('%')
        item['review_rating'] = float(data[0][indx1:indx2]) / 100.0 * 5.0
        review_list = []
        for indx in range(review_count):
            ratings_xpath = '//*[@id="customer-reviews"]/dl/dd[%d]//table[@class="ratings-table"]//div[@class="rating"]/@style' % (indx + 1)
            ratings = sel.xpath(ratings_xpath).extract()
            rating = 0.0
            for i in range(len(ratings)):
                indx1 = ratings[i].find('width:') + len('width:')
                indx2 = ratings[i].find('%', indx1)
                rating += float(ratings[i][indx1:indx2]) / 100.0 * 5.0
            if len(ratings) != 0:
                rating /= len(ratings)
            date_xpath = '//*[@id="customer-reviews"]/dl/dt[%d]/small[@class="date"]/text()' % (indx + 1)
            name_xpath = '//*[@id="customer-reviews"]/dl/dt[%d]/span/text()' % (indx + 1)
            title_xpath = '//*[@id="customer-reviews"]/dl/dt[%d]/h4/text()' % (indx + 1)
            content_xpath = '//*[@id="customer-reviews"]/dl/dd[%d]/text()' % (indx + 1)
            date = sel.xpath(date_xpath).extract()
            name = sel.xpath(name_xpath).extract()
            title = sel.xpath(title_xpath).extract()
            content = sel.xpath(content_xpath).extract()
            cont = ''
            for i in range(len(content)):
                cont += content[i]
            cont = cont.replace('\n', '')
            review_list.append({'rating':rating,
              'date':date[0],
              'name':name[0],
              'title':title[0],
              'content':cont})
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
