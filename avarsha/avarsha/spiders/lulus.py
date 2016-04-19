# -*- coding: utf-8 -*-
# @author: wanghaiyi

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = "lulus"

class LulusSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["lulus.com", "api.searchspring.net"]

    def __init__(self, *args, **kwargs):
        super(LulusSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        base_url = 'http://www.lulus.com'
        if sel.response.url.find('api.searchspring.net') == -1:
            items_xpath = ('//div[@class="mousetrap"]/'
                'a[contains(@class,"trap-link")]/@href')
        else:
            items_xpath = '//div[@class="item"]/p/a/@href'
        item_nodes = sel.xpath(items_xpath).extract()
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(item_url)
            request = scrapy.Request(item_url, callback=self.parse_item)
            requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        if sel.response.url.find('searchresults') == -1:
            base_url = 'http://www.lulus.com'
            nexts_xpath = ('//div[@class="nav"]//li[@class="next"]/'
                'a/@href')
            nexts = sel.xpath(nexts_xpath).extract()
            for path in nexts:
                list_url = path
                if path.find(base_url) == -1:
                    list_url = base_url + path
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
        else:
            page_num = 1
            url_tmp1 = 'https://api.searchspring.net/api/search/search.json?&q='
            url_tmp2 = sel.response.url[sel.response.url.find('q=') + 2:]
            test_url = url_tmp1 + url_tmp2 + '&websiteKey=b9b715891bc100cfd829b21046184251&page='
            url_tmp = test_url + str(page_num) + '&requestCount=0'
            content = urllib2.urlopen(url_tmp).read()
            idx1 = content.find('totalPages')
            idx2 = content.find('previousPage')
            total_page = int(content[idx1 + 12:idx2 - 2])
            for i in range(total_page):
                page_num = i
                url_tmp = test_url + str(page_num + 1) + '&requestCount=0'
                try:
                    content = urllib2.urlopen(url_tmp).read()
                except Exception as err1:
                    break
                else:
                    list_urls.append(url_tmp)
                    requests.append(scrapy.Request(url_tmp, callback=self.parse))
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//meta[contains(@property,"title")]/@content'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Lulus'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Lulus'

    def _extract_sku(self, sel, item):
        data = sel.response.url[sel.response.url.rfind('/') + 1:]
        if len(data) != 0:
            item['sku'] = data.strip('.html')

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@class="description"]/div/p/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]
        else:
            description_xpath = '//*[@name="description"]/@content'
            data = sel.xpath(description_xpath).extract()
            if len(data) != 0:
                item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//div/ul[@class="product slider"]/li/img/@src'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data
        else:
            imgs_xpath = '//div/ul[@class="product-images slider"]/li/img/@src'
            data = sel.xpath(imgs_xpath).extract()
            if len(data) != 0:
                item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//p[contains(@class,"color")]/span/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        items_size = []
        size_list_xpath = '//select[@id="size"]/option/text()'
        stock_sign_xpath = '//select[@id="size"]/option/@class'
        data = sel.xpath(size_list_xpath).extract()
        stock_sign = sel.xpath(stock_sign_xpath).extract()
        for i in range(len(stock_sign)):
            stock_sign[i] = stock_sign[i].strip('\n')
            stock_sign[i] = stock_sign[i].replace('\t', '')
        if len(data) != 0:
            if data[1].strip(' ') != 'Fit runs one size big.':
                for i in range(len(stock_sign)):
                    if ((stock_sign[i] != 'no-stock ') and
                            (stock_sign[i] != 'no-stock no-status')):
                        items_size.append(data[i + 1])
            else:
                for i in range(len(stock_sign)):
                    if ((stock_sign[i] != 'no-stock ')
                            and (stock_sign[i] != 'no-stock no-status')):
                        items_size.append(data[i + 2])
        if len(items_size) != 0:
            item['sizes'] = items_size

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//meta[contains(@name,"wanelo:product:price")]/@content'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$' , ''))

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//p[@class="price sale"]/@data-price'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_tmp = data[0]
            item['list_price'] = self._format_price('USD', price_tmp)

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        is_free_shipping_xpath = '//*[@id="shipOpts"]/span/text()'
        data = sel.xpath(is_free_shipping_xpath).extract()
        if len(data) != 0 and data[0] == 'Free':
            item['is_free_shipping'] = True

    def _extract_review_count(self, sel, item):
        review_count = 0
        sel = Selector(sel.response)
        review_count_xpath = '//div[@class="count"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if len(data) != 0:
            if data[len(data) - 1].rfind('(') != -1:
                data[len(data) - 1] = data[len(data) - 1].lstrip('(')
                data[len(data) - 1] = data[len(data) - 1].rstrip(')')
                review_count = int(data[len(data) - 1])
        if review_count != 0:
            item['review_count'] = review_count

    def _extract_review_rating(self, sel, item):
        review_rating = 0
        review_sum = 0
        review_count = 0
        sel = Selector(sel.response)
        review_count_xpath = '//div[@class="count"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if len(data) != 0:
            if data[len(data) - 1].rfind('(') != -1:
                data[len(data) - 1] = data[len(data) - 1].lstrip('(')
                data[len(data) - 1] = data[len(data) - 1].rstrip(')')
                review_count = int(data[len(data) - 1])
            rating_xpath = ('//div[@class="review"]/div[@class="stars"]'
                    '/div[contains(@class,"star-color")]/@style')
            ratings = sel.xpath(rating_xpath).extract()
            for i in range(0, review_count):
                ratings[i] = ratings[i].lstrip('width:')
                ratings[i] = ratings[i].rstrip('%;')
                ratings[i] = int(ratings[i]) / 20
                review_sum = review_sum + ratings[i]
            review_rating = float(review_sum) / float(review_count)
        if review_count != 0:
            item['review_rating'] = review_rating

    def _extract_best_review_rating(self, sel, item):
        item['max_review_rating'] = 5

    def _extract_review_list(self, sel, item):
        review_count = 0
        review_list = []
        review_sum = 0

        sel = Selector(sel.response)
        review_count_xpath = '//div[@class="count"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if len(data) != 0:
            if data[len(data) - 1].rfind('(') != -1:
                data[len(data) - 1] = data[len(data) - 1].lstrip('(')
                data[len(data) - 1] = data[len(data) - 1].rstrip(')')
                review_count = int(data[len(data) - 1])
            review_name_xpath = '//li[contains(@class,"name")]/text()'
            names = sel.xpath(review_name_xpath).extract()
            rating_xpath = ('//div[@class="review"]/div[@class="stars"]'
                    '/div[contains(@class,"star-color")]/@style')
            ratings = sel.xpath(rating_xpath).extract()
            for i in range(0, review_count):
                ratings[i] = ratings[i].lstrip('width:')
                ratings[i] = ratings[i].rstrip('%;')
                ratings[i] = int(ratings[i]) / 20
                review_sum = review_sum + ratings[i]
            review_rating = float(review_sum) / float(review_count)
            titles_xpath = '//div[contains(@class,"review")]/h3/text()'
            titles = sel.xpath(titles_xpath).extract()
            review_content_xpath = ('//div[contains(@class,"review")]/p/text()')
            review_contents = sel.xpath(review_content_xpath).extract()
            for j in range(len(names)):
                review_list.append({'rating':ratings[j], 'name':names[j],
                    'title':titles[j], 'content':review_contents[j]})
        if len(review_list) != 0:
            item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
