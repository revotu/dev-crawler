# -*- coding: utf-8 -*-
# @author: fsp

import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'forever21'

class Forever21Spider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["forever21.com"]

    def __init__(self, *args, **kwargs):
        super(Forever21Spider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = ''
        items_xpath = '//a[@class="pdpLink"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        base_url = 'http://www.forever21.com/Product/Category.aspx'
        nexts_xpath = '//li[@class="PagerOtherPageCells"]/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@class="product-title"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Forever21'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Forever21'

    def _extract_sku(self, sel, item):
        pcode_xpath = '//input[@name="ctl00$MainContent$hdProductId"]/@value'
        data = sel.xpath(pcode_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()

    def _extract_description(self, sel, item):
        des_xpath = '//span[@id="product_overview"]'
        data = sel.xpath(des_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_image_urls(self, sel, item):
        images_xpath = '//ul[@id="scroller"]//a/@rel'
        data = sel.xpath(images_xpath).extract()
        images = []
        if len(data) != 0:
            for content in data:
                image_start_index = content.find('largeimage: \'')
                if image_start_index != -1:
                    image_start_index += len('largeimage: \'')
                    image_end_index = content.find('\'', image_start_index)
                    image = content[image_start_index:image_end_index]
                    images.append(image)
            item['image_urls'] = images

    def _extract_colors(self, sel, item):
        color_xpath = ('//select[@name="ctl00$MainContent$ddlColor"]//'
            'option[not(@value="")]/text()')
        data = sel.xpath(color_xpath).extract()
        color_list = []
        if len(data) != 0:
            for line in data:
                color_list.append(line)
            item['colors'] = color_list

    def _extract_sizes(self, sel, item):
        size_list = []
        size_xpath = ('//select[@name="ctl00$MainContent$ddlSize"]//'
            'option[not(@value="")]/text()')
        data = sel.xpath(size_xpath).extract()
        if len(data) != 0:
            for line in data:
                size_list.append(line)
            item['sizes'] = size_list

    def _extract_list_price(self, sel, item):
        price_xpath = '//p[@class="was-now-price"]//text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            for line in data:
                start_index = line.find('$')
                index = line.find('"')
                if start_index != -1 and index == -1:
                    price = line[start_index + len('$'):]
                    item['list_price'] = self._format_price('USD', price)

    def _extract_price(self, sel, item):
        price_xpath = '//p[@class="product-price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', \
                (data[0].strip())[len('$'):])
        else:
            price_xpath = '//p[@class="was-now-price"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                for line in data:
                    start_index = line.find(':$')
                    if start_index != -1:
                        end_index = line.rfind('"')
                        price = line[start_index + len(':$'):end_index]
                        item['price'] = self._format_price('USD', price)

    def _extract_reviews(self, sel, item):
        review_count = 0
        review_rating = 0.0
        review_list = []

        pcode_xpath = '//input[@name="ctl00$MainContent$hdProductId"]/@value'
        data = sel.xpath(pcode_xpath).extract()
        key_str = self.__encrypt(data[0].strip())
        head_str = 'http://www.forever21.com/images/pwr/content/'
        tail_str = '-en_US-1-reviews.js'
        des_url = head_str + key_str + '/' + data[0].strip() + tail_str

        try :
            content = urllib2.urlopen(des_url).read()
        except Exception, e:
            print e
            item['max_review_rating'] = 5
            item['review_count'] = None
            item['review_rating'] = None
            item['review_list'] = None
            return
        else :
            tmp_review_count = content.count(',r:')
            pre_index = 0

            review_rating_sum = 0.0

            for j in range(tmp_review_count):
                rating_index = content.find(',r:', pre_index)
                if content[rating_index + len(',r:')] >= '0'\
                    and content[rating_index + len(',r:')] <= '5':
                    rating = int(content[rating_index + len(',r:')])
                else:
                    tmp_review_count -= 1
                    continue

                review_rating_sum += rating

                title_index = content.find(',h:', rating_index)
                title_index2 = content.find('\"', title_index + len(',h:\"') + 1)
                title = content[title_index + len(',h:\"'):title_index2]

                name_index = content.find(',n:', title_index)
                name_index2 = content.find('\"', name_index + len(',n:\"') + 1)
                name = content[name_index + len(',n:\"'):name_index2]

                date_index = content.find(',d:', name_index2)
                date_index2 = content.find('\"', date_index + len(',d:\"') + 1)
                date = content[date_index + len(',d:\"'):date_index2]
                date = date.replace('\\/', '/')

                reviews_index = content.find(',p:', name_index)
                reviews_index2 = content.find('\"', reviews_index + \
                    len(',p:\"') + 1)
                reviews = content[reviews_index + len(',p:\"'):reviews_index2]

                pre_index = reviews_index2

                review_list.append({'rating':rating,
                    'date':date,
                    'name':name,
                    'title':title,
                    'content':reviews})

            review_count = tmp_review_count
            review_rating = review_rating_sum / review_count

            item['max_review_rating'] = 5
            item['review_count'] = review_count
            item['review_rating'] = review_rating
            item['review_list'] = review_list

    def __encrypt(self, productId):
        sum = 0
        for i in range(len(productId)):
            charnum = ord(productId[i])
            charnum = charnum * abs(255 - charnum)
            sum += charnum
        sum = sum % 1023
        str2 = str(sum)
        for i in range(4 - len(str2)):
            str2 = '0' + str2
        result = str2[0:2] + '/' + str2[2:4]
        return result

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
