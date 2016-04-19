# -*- coding: utf-8 -*-
# @author: donglongtu

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'newyorkdress'

class NewyorkdressSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["newyorkdress.com", "newyorkdress.secureporte.com"]

    def __init__(self, *args, **kwargs):
        super(NewyorkdressSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx = url.find('search=')
        if idx != -1:
            para = url[idx:]
            para_call = (para.replace('=', '_').replace('+', '_').replace('&',
                '_').replace('-', '_').replace('|', '_'))
            url = ('http://newyorkdress.secureporte.com/Search.html?%s&adeptNav'
                'Enabled=&callback=jsonpCallback_Search_html_%s_adeptNavEnable'
                'd_' % (para, para_call))
        return url

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            idx = list_url.find('search=')
            if idx != -1:
                para = list_url[idx:]
                para_call = (para.replace('=', '_').replace('+', '_').replace(
                    '&', '_').replace('-', '_').replace('|', '_'))
                list_url = ('http://newyorkdress.secureporte.com/Search.html?%s'
                    '&adeptNavEnabled=&callback=jsonpCallback_Search_html_%s_a'
                    'deptNavEnabled_' % (para, para_call))
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests


    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.newyorkdress.com/'
        items_xpath = '//*[@class="preview"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.newyorkdress.com'
        nexts_xpath = ('//*[@class="sb_pag"]/ul/li/a/@href | //*[@id="divPager"'
            ']/li/a/@href | //*[@class="adeptajax pagerlink"]/@href')

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = ('//*[@id="ctl00_ContentPlaceHolder1_lblItemName"]'
            '/h2/text()')
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Newyorkdress'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@itemprop="brand"]/@content'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        index1 = sel.response.url.rfind('/')
        index2 = sel.response.url.find('html')
        data = sel.response.url[index1 + 1 : index2 - 1]
        if len(data) != 0:
            item['sku'] = data

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        desc_xpath = '//*[@id="ctl00_ContentPlaceHolder1_lblDescription"]/p'
        data = sel.xpath(desc_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//*[@rel="zoom-id:Zoomer3"]/@rev'
        data = sel.xpath(imgs_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data
        else :
            imgs_xpath = '//*[@id="Zoomer3"]/@href'
            data = sel.xpath(imgs_xpath).extract()
            if len(data) != 0:
                item['image_urls'] = data

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price_number = data[0].strip()[len('$'):]
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_xpath = ('//*[@style="color:#ffffff; font-size:14px; pad'
            'ding: 0 0 5 0"]/text()')
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
        review_count_xpath = '//span[@itemprop="reviewCount"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if(len(data) == 0):
            item['review_count'] = 0
            return []
        review_count = int(data[0])
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        review_rating_xpath = '//div[@class="product-rating-info"]/p/span[@itemprop="ratingValue"]/text()'
        data = sel.xpath(review_rating_xpath).extract()
        item['review_rating'] = float(data[0])
        ratings_xpath = ('//table[@id="ctl00_ContentPlaceHolder1_reviewsDisplay_dlReviews"]//tr' +
        '//meta[@itemprop="ratingValue"]/@content')
        dates_xpath = ('//table[@id="ctl00_ContentPlaceHolder1_reviewsDisplay_dlReviews"]//tr' +
        '//meta[@itemprop="datePublished"]/@content')
        names_xpath = ('//table[@id="ctl00_ContentPlaceHolder1_reviewsDisplay_dlReviews"]//tr' +
        '//span[@itemprop="author"]/text()')
        titles_xpath = ('//table[@id="ctl00_ContentPlaceHolder1_reviewsDisplay_dlReviews"]//tr' +
        '//span[@itemprop="name"]/text()')
        contents_xpath = ('//table[@id="ctl00_ContentPlaceHolder1_reviewsDisplay_dlReviews"]//tr' +
        '//span[@itemprop="description"]')
        ratings = sel.xpath(ratings_xpath).extract()
        dates = sel.xpath(dates_xpath).extract()
        names = sel.xpath(names_xpath).extract()
        titles = sel.xpath(titles_xpath).extract()
        contents = sel.xpath(contents_xpath).extract()
        review_list = []
        for indx in range(len(ratings)):
            ratings[indx] = float(ratings[indx])
            indx1 = contents[indx].find('itemprop') + len('itemprop')
            indx2 = contents[indx].find('>', indx1) + len('>')
            indx3 = contents[indx].find('</span', indx2)
            review_list.append({'rating':ratings[indx],
              'date':dates[indx],
              'name':names[indx],
              'title':titles[indx],
              'content':contents[indx][indx2:indx3]})
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
