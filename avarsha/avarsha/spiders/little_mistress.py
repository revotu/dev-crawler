# -*- coding: utf-8 -*-
# @author: hanzhiqiang

import re

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'little_mistress'

class Little_mistressSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["little-mistress.com"]
    flag = False

    def __init__(self, *args, **kwargs):
        super(Little_mistressSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx = url.find('#')
        if(idx != -1):
            _var1 = ('http://www.little-mistress.com/'
                'ajax/getProductListings?base_url=')
            _var2 = ('&page_type=productlistings&'
                'page_variant=show&parent_category_id[]=')
            _var3 = '&categories_id[]='
            _var4 = '&all_upcoming_flag[]=78&show=&sort=&page=1'
            _var5 = '&tags_id[]='
            category_id, tags_id, base_url = self._get_real_url(idx, url)
            for var in url[idx + 1:].split(':'):
                tags_id = tags_id + _var5 + str(var[1:])
            url = _var1 + base_url + _var2 + str(category_id) + \
                _var3 + str(category_id) + _var4 + tags_id
            url = url.replace('[]', '%5B%5D')
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.little-mistress.com'
        items_xpath = '//a[@class="product_title"]/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        body = sel.response.body.split('\n')
        if(len(body) == 1 and body[0].find('product_title') == -1):
            return requests
        _url = sel.response.url
        if(_url.find('ajax') != -1):
            idx1 = _url.find('&page=')
            idx2 = _url.find('&', idx1 + len('&page='))
            if(idx2 == -1):
                idx2 = len(_url)
            page = _url[idx1 + len('&page='):idx2]
            list_url = \
                _url[:idx1 + len('&page=')] + str(int(page) + 1) + _url[idx2:]
        elif(_url.find('/search/') != -1):
            list_url = self._get_search_real_url(_url)
        else:
            _var1 = ('http://www.little-mistress.com/'
                'ajax/getProductListings?base_url=')
            _var2 = ('&page_type=productlistings&'
                'page_variant=show&parent_category_id[]=')
            _var3 = '&categories_id[]='
            _var4 = '&all_upcoming_flag[]=78&show=&sort=&page=2'
            category_id, tags_id, base_url = \
                self._get_real_url(-1, sel.response.url)
            list_url = _var1 + base_url + _var2 + str(category_id) + \
                _var3 + str(category_id) + _var4 + tags_id
        list_url = list_url.replace('[]', '%5B%5D')
        list_urls.append(list_url)
        request = scrapy.Request(list_url, callback=self.parse)
        requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@id="product_title"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data_re = re.compile('<[^<>]+>|\n+|\r+|\t+|  +')
            item['title'] = data_re.sub('', data[0])

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Little-mistress'

    def _extract_brand_name(self, sel, item):
        product_title_xpath = '//span[@id="product_title"]/text()'
        product_title = sel.xpath(product_title_xpath).extract()
        brand_name_xpath = '//span[@class="product_title_brand"]/text()'
        brand_name = sel.xpath(brand_name_xpath).extract()
        if len(brand_name) != 0:
            for _data in brand_name:
                _brand_name = _data.strip()
                if(product_title[0].find(_brand_name) != -1):
                    item['brand_name'] = _brand_name
                    break

    def _extract_sku(self, sel, item):
        _sku = ''
        for line in sel.response.body.split('\n'):
            idx = line.find('"product":{')
            if(idx != -1):
                idx1 = line.find('description":"')
                if(idx1 != -1):
                    idx2 = line.find('",', idx1)
                    _sku = line[idx1 + len('description":"'):idx2]
        item['sku'] = str(_sku)

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_details_xpath = '//div[@id="details_tab_content"]//*'
        data_details = sel.xpath(description_details_xpath).extract()
        description_summary_xpath = '//div[@id="summary_tab_content"]//*'
        data_summary = sel.xpath(description_summary_xpath).extract()
        _description = ''
        if len(data_details) != 0:
            _description = data_details[0]
        if len(data_summary) != 0:
            _description = ''.join([_description, data_summary[0]])
        item['description'] = _description

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs = []
        image_url = ''
        imgs_url_xpath = '//div[@id="product_img"]//li/a/@href'
        imgs_url2_xpath = '//div[@id="product_img"]/a/@href'
        data_imgs = sel.xpath(imgs_url_xpath).extract()
        data_imgs2 = sel.xpath(imgs_url2_xpath).extract()
        if len(data_imgs) != 0:
            for image_url in data_imgs:
                if(image_url.find('http:') == -1):
                    image_url = 'http:' + image_url
                imgs.append(image_url)
        elif(len(data_imgs2) != 0):
            image_url = data_imgs2[0]
            imgs.append(image_url)
        item['image_urls'] = imgs

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        symbol_xpath = (
            '//span[@id="product_price_sale"]//span[@class="inc"]'
            '//span[not(@style)]/@class')
        price_xpath = (
            '//span[@id="product_price_sale"]//span[@class="inc"]'
            '//span[not(@style)]/@content')
        symbol = sel.xpath(symbol_xpath).extract()
        price = sel.xpath(price_xpath).extract()
        _symbol = ''
        _price = ''
        if len(symbol) != 0:
            _symbol = symbol[0]
        if len(price) != 0:
            _price = price[0]
            item['price'] = self._format_price(_symbol, _price)

    def _extract_list_price(self, sel, item):
        symbol_xpath = (
            '//span[@id="product_price_was"]//span[@class="inc"]'
            '//span[not(@style)]/@class')
        list_price_xpath = (
            '//span[@id="product_price_was"]//span[@class="inc"]'
            '//span[not(@style)]/text()')
        symbol = sel.xpath(symbol_xpath).extract()
        list_price = sel.xpath(list_price_xpath).extract()
        _symbol = ''
        _list_price = ''
        if len(symbol) != 0:
            _symbol = symbol[0]
        if len(list_price) != 0:
            _list_price = list_price[0]
            data_re = re.compile(r'&nbsp;|\n+|\r+|\t+|  +|[£$€¥]|Kr|kr|zl|sf')
            _list_price = data_re.sub('', _list_price)
            item['list_price'] = self._format_price(_symbol, _list_price)

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
        review_count_xpath = '//span[class="votes"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        if(len(data) == 0):
            item['review_count'] = 0
            return []
        else:
            review_count = int(data[0])
            print review_count
            item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        review_rating_xpath = '//span[class="average"]/text()'
        data = sel.xpath(review_count_xpath).extract()
        item['review_rating'] = float(data[0])
        date = []
        name_xpath = '//div[@class="product_reviews_author"]/text()'
        name = sel.xpath(name_xpath).extract()
        title_xpath = '//div[@class="col col_9 advanced_review_title"]/text()'
        title = sel.xpath(title_xpath).extract()
        conts_xpath = '//div[@class="review_content"]/p/text()'
        conts = sel.xpath(conts_xpath).extract()
        rate_container_xpath = '//div[@class="col col_3 t_col_5 advanced_review_stars"]'
        rate_container = sel.xpath(rate_container_xpath).extract()
        rating = []
        for i in range(len(rate_container)):
            rating.append(5.0 - rate_container[i].count('fa fa-star-o'))

        num_inuse = min(len(rating), len(name), len(title), len(conts))
        review_list = []
        for i in range(num_inuse):
            review_list.append({'rating':rating[i],
              'date':'',
              'name':name[i],
              'title':title[i],
              'content':conts[i]})
        item['review_list'] = review_list

    def _get_real_url(self, idx, url):
        if(idx == -1):
            idx = len(url)
        idx1 = url.find('.com')
        idx2 = url.rfind('-c')
        idx3 = url.find('/', idx2)
        category_id = ''
        tags_id = ''
        base_url = url[idx1 + len('.com') + 1:idx].replace('/', '%2F')
        if(idx3 != -1):
            category_id = url[idx2 + len('-c'):idx3]
        elif(idx != -1):
            category_id = url[idx2 + len('-c'):idx]
        else:
            category_id = url[idx2 + len('-c'):len(url)]
        return category_id, tags_id, base_url

    def _get_search_real_url(self, url):
        idx = url.find('search/')
        base_url = ''
        keywords = ''
        if(idx != -1):
            base_url = url[idx:].replace('/', '%2F')
            keywords = url[idx + len('search/'):]
        _url1 = ('http://www.little-mistress.com/ajax/getProductListings'
            '?base_url=')
        _url2 = ('&page_type=productlistings&page_variant=show'
            '&all_upcoming_flag[]=78&keywords=')
        _url3 = '&show=&sort=&page=2'
        _search_real_url = _url1 + base_url + _url2 + keywords + _url3
        return _search_real_url

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
