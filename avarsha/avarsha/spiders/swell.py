# -*- coding: utf-8 -*-
# author fsp

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'swell'

class SwellSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["swell.com"]

    def __init__(self, *args, **kwargs):
        super(SwellSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        if url.find('search#') != -1:
            key_start_index = url.find('w=')
            key_end_index = url.find('&', key_start_index)
            if key_end_index != -1:
                key = url[key_start_index + len('w='):key_end_index]
            else:
                key = url[key_start_index + len('w='):]
            url_head = 'http://surf.swell.com/search?'
            url_tail = ''    # &ts=ajax'
            return url_head + 'w=' + key + url_tail
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = ''
        items_xpath = ('//div[@class="prod-list"]//a[@style="display: block;"]'
            '/@href | //div[@class="prodName"]/a/@title')

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def _find_items_from_list_page(self, sel, base_url, items_xpath, item_urls):
        item_nodes = sel.xpath(items_xpath).extract()
        requests = []
        for path in item_nodes:
            item_url = base_url + path
            item_urls.append(item_url)
            requests.append(scrapy.Request(item_url, callback=self.parse_item))
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//a[@id="pagerpagenumnext"]/@href'

        # don't need to change this line //a[@class="pagenum"]/@href |
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

#     def _find_nexts_from_list_page(
#         self, sel, base_url, nexts_xpath, list_urls):
#         nexts = sel.xpath(nexts_xpath).extract()
#         requests = []
#         for path in nexts:
#             list_url = path.replace('#?', '?')
#             if path.find(base_url) == -1:
#                 list_url = base_url + path
#             list_urls.append(list_url)
#             request = scrapy.Request(list_url, callback=self.parse)
#             requests.append(request)
#         return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="prod-Name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Swell'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//span[@itemprop="brand"]/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        pcode_xpath = '//span[@itemprop="productID"]/text()'
        data = sel.xpath(pcode_xpath).extract()
        try:
            productId = data[0].strip()
        except Exception, e:
            print e
        if len(data) != 0:
            item['sku'] = productId

    def _extract_description(self, sel, item):
        des_xpath = '//div[@itemprop="description"]//text()'
        data = sel.xpath(des_xpath).extract()
        des = data[0]
        for i in range(len(data)):
            des += data[i].strip('\n').strip('\t').strip()
        item['description'] = des.strip()

    def _extract_image_urls(self, sel, item):
        images_xpath = ('//div[@class="product-layout-left"]//'
            'a[@onmouseover]/@zoomimg | //div[@class="product-main-image"]//'
            'a[@zoomimg]/@zoomimg')
        data = sel.xpath(images_xpath).extract()
        images = []
        for i in range(len(data)):
            images.append('http://content.swell.com' + data[i])
        if len(images) != 0:
            item['image_urls'] = images

    def _extract_colors(self, sel, item):
        color_xpath = '//span[@class="swatch-itm-lbl"]/text()'
        data = sel.xpath(color_xpath).extract()
        color_list = []
        if len(data) != 0:
            for line in data:
                color_list.append(line)
            item['colors'] = color_list

    def _extract_sizes(self, sel, item):
        size_list = []
        size_xpath = '//div[@class="prod-size-item"]/a/span/text()'
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            for line in data:
                size_list.append(line)
            item['sizes'] = size_list

    def _extract_list_price(self, sel, item):
        price_xpath = '//span[@class="defPrice"]/span[@class="Amount"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_index = data[0].find('$')
            if price_index != -1:
                item['list_price'] = self._format_price('USD', \
                    data[0][price_index + len('$'):])
            else:
                item['list_price'] = self._format_price('USD', data[0])

    def _extract_price(self, sel, item):
        price_xpath = '//span[@itemprop="price"]/span[@class="Amount"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_index = data[0].find('$')
            if price_index != -1:
                item['price'] = self._format_price('USD', \
                    data[0][price_index + len('$'):])
            else:
                item['price'] = self._format_price('USD', data[0])

    def _extract_reviews(self, sel, item):
        review_count = 0
        review_rating = 0
        review_list = []

        review_count_xpath = '//span[@class="count"]/text()'
        data = sel.xpath(review_count_xpath).extract()

        if len(data) != 0:
            review_count = int(data[0])

            # assume reviews in one page
            review_rating_xpath = ('//span[@class="pr-rating pr-rounded'
                ' average"]/text()')
            review_rating = float(sel.xpath(review_rating_xpath).extract()[0])

            review_name_xpath = ('//p[@class="pr-review-author-name"]'
                '/span/text()')
            names = sel.xpath(review_name_xpath).extract()

            review_date_xpath = ('//div[@class="pr-review-author-date'
                ' pr-rounded"]/text()')
            dates = sel.xpath(review_date_xpath).extract()

            rating_xpath = '//span[@class="pr-rating pr-rounded"]/text()'
            ratings = sel.xpath(rating_xpath).extract()

            titles_xpath = '//p[@class="pr-review-rating-headline"]/text()'
            titles = sel.xpath(titles_xpath).extract()

            review_content_xpath = '//p[@class="pr-comments"]/text()'
            review_contents = sel.xpath(review_content_xpath).extract()

            for j in range(len(names)):
                rating = float(ratings[j])
                review_list.append({'rating':rating,
                    'date':dates[j],
                    'name':names[j],
                    'title':titles[j],
                    'content':review_contents[j]})
            item['max_review_rating'] = 5
            item['review_count'] = review_count
            item['review_rating'] = review_rating
            item['review_list'] = review_list

        item['max_review_rating'] = 5
        item['review_count'] = None
        item['review_rating'] = None
        item['review_list'] = None

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
