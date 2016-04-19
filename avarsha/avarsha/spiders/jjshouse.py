# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline
import urllib2
from avarsha_spider import AvarshaSpider
from scrapy.selector import Selector

_spider_name = "jjshouse"

class JjshouseSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["jjshouse.com"]

    def __init__(self, *args, **kwargs):
        super(JjshouseSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = 'http://www.jjshouse.com'
        if sel.response.url.find('search.php') == -1:
            items_xpath = '//div[@class="cat-bottom"]/\
                div[@class="cat-prod-list"]//h2//a//@href'
        else:
            items_xpath = ('//div[@class="cat-prod-list search"]'
                '//div[@class="catpl-group catpl-group-237x320 clearfix"]'
                '//div[@class="catpl-prod"]/div[@class="pic"]/a/@href')

        # don't need to change this line
        return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.jjshouse.com'
        nexts_xpath = '//div[@class="show_skip clearfix"]/\
            div[@class="page"]//a//@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="prod-info-title"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Jjshouse'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Jjshouse'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="prod-info-title"]/h1/span/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][1:]

    def _extract_features(self, sel, item):
        features_xpath = (
            '//table[@class="goods_attribute_new"]//tr//td/text()')
        data = sel.xpath(features_xpath).extract()
        if len(data) != 0:
            features = {}
            idx = 0
            while idx < len(data):
                features[data[idx]] = data[idx + 1]
                idx += 2
            item['features'] = features

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="goods_desc"]/p//text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line.strip()
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        image_url_xpath = '//div[@class="magnify"]//a//@href'
        data = sel.xpath(image_url_xpath).extract()
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        colors_xpath = '//div[@class="pis-color-box clearfix color"]\
            //a[@class="pis-color-a"]/dl/dd/text()'
        data = sel.xpath(colors_xpath).extract()
        if len(data) != 0:
            idx = 0
            idx1 = 0
            while idx1 < len(data):
                tdata = data[idx1].replace(' ', '')\
                    .replace('\n', '')
                if len(tdata) != 0:
                    data[idx] = tdata
                    idx += 1
                idx1 += 1
            data = data[:idx]
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//table[@class="measurement"]/tbody//tr/td[1]/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = (
            '//strong[@class="shop_price"]/span[@id="id_shop_price"]//text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            if len(data) == 2:
                item['price'] = 'USD ' + data[0] + data[1]
            else:
                item['price'] = 'USD' + data[0]

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//span[@id="page_common_list_price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            idx = data[0].find('$')
            if idx != -1:
                list_price_num = data[0][idx + 1:].strip()
                item['list_price'] = self._format_price('USD', list_price_num)

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
        count_xpath = '//a[@class="comment_count"]/text()'
        data = sel.xpath(count_xpath).extract()
        review_count = 0
        if len(data) == 0:
            item['review_count'] = 0
            return []
        else:
            data[0] = data[0].replace('(', '')
            data[0] = data[0].replace(')', '')
            review_count = int(data[0])
        item['review_count'] = review_count
        if review_count == 0:
            return []
        max_review_rating = 5
        item['max_review_rating'] = max_review_rating
        rating_xpath = '//div[@class="win_dress_rate"]/em/text()'
        data = sel.xpath(rating_xpath).extract()
        review_rating = 5.0
        if len(data) != 0:
            review_rating = float(data[0])
        item['review_rating'] = review_rating
        url = sel.response.url
        idx = url.rfind('-')
        base_url = 'http://www.jjshouse.com'
        idx0 = url.find(base_url) + len(base_url)
        head_url = url[idx0:idx]
        tail_url = url[idx:]
        tail_url = tail_url.replace('g', 'p')
        review_url = base_url + '/reviews' + head_url + '-cid2' + tail_url
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        review_list = []
        pagenum = 1
        while 'class="ask"' in content:
            sel = Selector(text=content)
            review_rating_xpath = '//div[@class="forComments"]/div[@class="ask"]/span[1]/@class'
            review_date_xpath = '//div[@class="forComments"]/div[@class="ask"]/span[2]/text()'
            review_name_xpath = '//div[@class="forComments"]/div[@class="ask"]/strong/text()'
            review_content_xpath = '//div[@class="forComments"]/div[@class="askContent"]/p[@class="no_translated"]'
            review_rating = sel.xpath(review_rating_xpath).extract()
            review_date = sel.xpath(review_date_xpath).extract()
            review_name = sel.xpath(review_name_xpath).extract()
            review_content = sel.xpath(review_content_xpath).extract()
            review_num = min(len(review_rating), len(review_date), len(review_name), len(review_content))
            if review_num != 0:
                for i in range(review_num):
                    rate = review_rating[i].replace('star star_', '')
                    ratings = float(rate)
                    dates = review_date[i]
                    names = review_name[i].replace('By ', '')
                    conts = review_content[i]
                    indx1 = conts.find('p')
                    indx2 = conts.find('>', indx1) + len('>')
                    indx3 = conts.find('</p>', indx2)
                    conts = conts[indx2:indx3]
                    conts = conts.replace('<br>\n', '')
                    review_list.append({'rating':ratings,
                                      'date':dates,
                                      'name':names,
                                      'title':'',
                                      'content':conts})
            pagenum += 1
            review_url0 = review_url + '?page=' + str(pagenum)
            request = urllib2.Request(review_url0)
            response = urllib2.urlopen(request)
            content = ''
            content = response.read()
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
