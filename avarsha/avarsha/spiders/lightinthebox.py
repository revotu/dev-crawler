# -*- coding: utf-8 -*-
# author fsp

import urllib2
import scrapy.cmdline

from scrapy import log
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'lightinthebox'

class LightintheboxSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["lightinthebox.com"]

    def __init__(self, *args, **kwargs):
        super(LightintheboxSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        new_url = url[:url.find('#')]
        return new_url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = ''
        items_xpath = '//dd[@class="prod-name"]//a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//ul[@class="clearfix"]//a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="widget prod-info-title"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Lightinthebox'

    def _extract_brand_name(self, sel, item):
        feature_keys_xpath = (
            '//table[@class="table table-condensed mini-text "]/tr/th/text()')
        feature_values_xpath = (
            '//table[@class="table table-condensed mini-text "]/tr/td')
        feature_keys = sel.xpath(feature_keys_xpath).extract()
        feature_values = sel.xpath(feature_values_xpath).extract()

        if len(feature_keys) != 0 and len(feature_values) != 0:
            for i in range(len(feature_keys)):
                if feature_keys[i].strip() == 'Brand':
                    tmp_sel = Selector(text=feature_values[i].strip())
                    tmp_value_list = tmp_sel.xpath('//text()').extract()
                    value = ''
                    for text in tmp_value_list:
                        value += ',' + text
                    item['brand_name'] = value.replace(',  ', '').strip()
                    break;
        if item['brand_name'] == '':
            item['brand_name'] = 'lightinthebox'
    def _extract_sku(self, sel, item):
        pcode_xpath = '//span[@class="item-id"]/text()'
        data = sel.xpath(pcode_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()[1:]

    def _extract_features(self, sel, item):
        feature_dict = {}

        feature_keys_xpath = (
            '//table[@class="table table-condensed mini-text "]/tr/th/text()')
        feature_values_xpath = (
            '//table[@class="table table-condensed mini-text "]/tr/td')
        feature_keys = sel.xpath(feature_keys_xpath).extract()
        feature_values = sel.xpath(feature_values_xpath).extract()

        if len(feature_keys) != 0 and len(feature_values) != 0:
            for i in range(len(feature_keys)):
                tmp_sel = Selector(text=feature_values[i].strip())
                tmp_value_list = tmp_sel.xpath('//text()').extract()
                value = ''
                for text in tmp_value_list:
                    value += ',' + text
                feature_dict[feature_keys[i]] = value.replace(',  ', '').strip()
        item['features'] = feature_dict

    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        size_chart_xpath = '//div[@class="chartContainer 0"]/table'
        data = sel.xpath(size_chart_xpath).extract()
        if len(data) != 0:
            item['size_chart'] = data[0]

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        images = []

        images_xpath = ('//li[@class="item current"]//img/@data-normal'
            ' | //li[@class="item "]//img/@data-normal'
            ' | //li[@class="item"]//img/@data-normal'
            ' | //div[@class="item current"]//img/@data-normal'
            ' | //div[@class="item "]//img/@data-normal'
            ' | //div[@class="item"]//img/@data-normal')
        data = sel.xpath(images_xpath).extract()
        h2m_image_xpath = '//div[@class="widget how-to-measure"]/img/@src'
        h2m_image_data = sel.xpath(h2m_image_xpath).extract()
        m_image_xpath = '//div[@class="widget prod-note-marketing"]/div/img/@src'
        m_image_data = sel.xpath(m_image_xpath).extract()

        if len(data) != 0:
            images = data
        if len(h2m_image_data) != 0:
            images.append(h2m_image_data[0])
        if len(m_image_data) != 0:
            images.append(m_image_data[0])
        item['image_urls'] = images

    def _extract_basic_options(self, sel, item):
        color_list = []
        size_list = []

        # The class attritube may be end up with 0 to 2 spaces
        test1_xpath = ('//ul[@class="widget attributes  "]/li[1]'
            '//option[@value=""]/text()')
        test1_data = sel.xpath(test1_xpath).extract()
        test2_xpath = ('//ul[@class="widget attributes "]/li[1]'
            '//option[@value=""]/text()')
        test2_data = sel.xpath(test2_xpath).extract()
        test3_xpath = ('//ul[@class="widget attributes"]/li[1]'
            '//option[@value=""]/text()')
        test3_data = sel.xpath(test3_xpath).extract()
        if len(test1_data) != 0:
            real_class = '"widget attributes  "'
        elif len(test2_data) != 0:
            real_class = '"widget attributes "'
        elif len(test3_data) != 0:
            real_class = '"widget attributes"'
        else:
            real_class = ''

        if real_class != '':
            real_path = ('//ul[@class=' + real_class + ']/li[1]'
                + '//option[@value=""]/text()')
            data = sel.xpath(real_path).extract()
            if data[0].find('Color') != -1:
                color_xpath = ('//ul[@class=' + real_class + ']/li[1]'
                    + '//option[not(@value="")]/text()')
                data = sel.xpath(color_xpath).extract()
                if len(data) != 0:
                    for line in data:
                        color_list.append(line.strip())
                    item['colors'] = color_list

                size_xpath = ('//ul[@class=' + real_class + ']/li[2]'
                    + '//option[not(@value="")]/text()')
                data = sel.xpath(size_xpath).extract()
                if len(data) != 0:
                    for line in data:
                        size_list.append(line.strip())
                    item['sizes'] = size_list
            elif data[0].find('Size') != -1:
                size_xpath = ('//ul[@class=' + real_class + ']/li[1]'
                    + '//option[not(@value="")]/text()')
                data = sel.xpath(size_xpath).extract()
                if len(data) != 0:
                    for line in data:
                        size_list.append(line.strip())
                    item['sizes'] = size_list

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//strong[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD',
                (data[0].strip())[len('$ '):])

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="price-left"]//del/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            price_index = data[0].strip().rfind(' ') + 1
            item['list_price'] = self._format_price('USD',
                data[0][price_index:])

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        pass

    def _extract_reviews(self, sel, item):
        review_count, review_rating, review_list = self.__collect_reviews(sel)
        if review_count != None:
            item['max_review_rating'] = 5
            item['review_count'] = review_count
            item['review_rating'] = review_rating
            item['review_list'] = review_list

    def __collect_reviews(self, sel):
        review_count = 0
        review_rating = 0.0
        review_list = []

        review_url_xpath = '//div[@class="widget view-sell-all"]/a/@href'
        review_url = sel.xpath(review_url_xpath).extract()
        if len(review_url) == 0:
            return None, None, None
        try :
            content = urllib2.urlopen(review_url[0]).read()
        except:
            self.log('Cannot open url:' + review_url[0], log.DEBUG)
            return None, None, None
        else :
            sel = Selector(text=content)

            review_rating_xpath = '//strong[@class="score"]/text()'
            data = sel.xpath(review_rating_xpath).extract()
            review_rating = float(data[0].strip())

            review_count_xpath = '//a[@class="reviewNums"]/text()'
            review_count_content = \
                (sel.xpath(review_count_xpath).extract())[0].strip()
            review_count_end_index = review_count_content.find(' ')
            review_count = \
                int(review_count_content[len('('):review_count_end_index])

            review_page_url_xpath = '//li[@class="pageIndex"]/a[1]/@href'
            data = sel.xpath(review_page_url_xpath).extract()
            if len(data) != 0:
                review_page_tmpurl = data[0].strip()
                review_page_url_prefix = review_page_tmpurl[:-1]

                review_page_num_xpath = \
                    '//li[@class="pageIndex"]/a[last()]/text()'
                review_page_num = \
                    int((sel.xpath(review_page_num_xpath).extract())[0].strip())
            else:
                review_list += self.__review_list_in_one_page(sel)
                return review_count, review_rating, review_list

            for page in range(review_page_num - 1):
                review_page_url = review_page_url_prefix + str(1 + page)
                try :
                    content = urllib2.urlopen(review_page_url).read()
                    sel = Selector(text=content)
                    review_list += self.__review_list_in_one_page(sel)
                except:
                    self.log(
                        'Cannot open review URL:' + review_page_url, log.DEBUG)
                    return None, None, None

            return review_count, review_rating, review_list

    def __review_list_in_one_page(self, sel):
        review_list = []

        rating_xpath = '//ul[@class="reviewerInfo"]/li/span[@title]/@title'
        ratings = sel.xpath(rating_xpath).extract()

        review_name_xpath = '//cite[@class="b"]/text()'
        names = sel.xpath(review_name_xpath).extract()

        review_date_xpath = '//cite[@class="lightGray"]/text()'
        dates = sel.xpath(review_date_xpath).extract()

        review_content_xpath = '//p[@class="reviewInfo"]'
        review_contents = sel.xpath(review_content_xpath).extract()

        for j in range(len(names)):
            rating = float((ratings[j].strip())[0])
            review_list.append({
                'rating':rating,
                'date':dates[j],
                'name':names[j],
                'title':'',
                'content':review_contents[j]})
        return review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
