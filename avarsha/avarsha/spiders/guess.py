# -*- coding: utf-8 -*-
# @author: donglongtu

import re
import urllib2

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'guess'

class GuessSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["shop.guess.com"]

    def __init__(self, *args, **kwargs):
        super(GuessSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://shop.guess.com'
        items_xpath = '//*[@class="prodImg"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://shop.guess.com'
        nexts_xpath = '//*[@class="pagination pull-right"]/ul/li/a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="rightdetails span4"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Guess'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Guess'

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="productSKU"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].strip()[len('Style: #'):]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//*[@id="collapseOne"]/div'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//*[@property="og:image"]/@content'
        data = sel.xpath(imgs_xpath).extract()
        imgs_url_list = []
        prefix = 'http://s7d5.scene7.com/is/image/Guess/'
        suffix = '?wid=1200&hei=1200&fmt=jpg'
        if len(data) != 0:
            index = data[0].strip().find('?')
            imgs_set_url = data[0].strip()[:index] + '_IS?req=set,json,UTF-8'
            content = urllib2.urlopen(imgs_set_url).read()
            img_set_reg = re.compile(r'Guess/([\w-]+?)\"},\"dx\"')
            img_set = img_set_reg.findall(content)
            for img in img_set:
                imgs_url_list.append(prefix + img + suffix)
            item['image_urls'] = imgs_url_list

    def _extract_colors(self, sel, item):
        color_list_xpath = '//*[@class="row-fluid colorbox"]/ul/li/a/img/@alt'
        data = sel.xpath(color_list_xpath).extract()
        if len(data) != 0:
            item['colors'] = []
            for color in data:
                if color.strip() != '':
                    item['colors'].append(color.strip())

    def _extract_sizes(self, sel, item):
        size_list_xpath = '//*[@id="sizeSelectionList"]/li/a/text()'
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = []
            for size in data:
                if size.strip() != '':
                    item['sizes'].append(size.strip())

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_reg = re.compile(r'\"productCurrentPrice\": \"(.+?)\",')
        data = price_reg.findall(sel.response.body)
        if len(data) != 0:
            price_number = data[0].strip()
            item['price'] = self._format_price('USD', price_number)

    def _extract_list_price(self, sel, item):
        list_price_reg = re.compile(r'\"productOriginalPrice\": \"(.+?)\",')
        data = list_price_reg.findall(sel.response.body)
        if len(data) != 0:
            list_price_number = data[0].strip()
            list_price = self._format_price('USD', list_price_number)
            if list_price != item['price']:
                item['list_price'] = list_price

    def _extract_low_price(self, sel, item):
        pass

    def _extract_high_price(self, sel, item):
        pass

    def _extract_is_free_shipping(self, sel, item):
        pass

    def _extract_reviews(self, sel, item):
        review_count = 0
        review_rating = 0
        review_list = []
        review_sum = 0

        product_token_xpath = '//div[@class="tfc-fitrec-product"]/@id'
        product_token = sel.xpath(product_token_xpath).extract()
        first_review_url = ('http://api.bazaarvoice.com/data/batch.json?passk'
                'ey=9u5bt4k1uinp95si5bctgefh2&apiversion=5.5&displaycode'
                '=11616-en_us&resource.q0=products&filter.q0=id%3Aeq'
                '%3A' + product_token[0] + '_us&stats.q0=reviews&fi'
                'lteredstats.q0=reviews&filter_reviews.q0=contentlo'
                'cale%3Aeq%3Aen_CA%2Cen_US%2Cfr_CA&filter_reviewcom'
                'ments.q0=contentlocale%3Aeq%3Aen_CA%2Cen_US%2Cfr_C'
                'A&resource.q1=reviews&filter.q1=isratingsonly%3Aeq'
                '%3Afalse&filter.q1=producti'
                'd%3Aeq%3A' + product_token[0] + '_us&filter.q1=co'
                'ntentlocale%3Aeq%3Aen_CA%2Cen_US%2Cfr_CA&sort.q1'
                '=submissiontime%3Adesc&stats.q1=reviews&filtered'
                'stats.q1=reviews&include.q1=authors%2Cproducts%2'
                'Ccomments&filter_reviews.q1=contentlocale%3Aeq%3'
                'Aen_CA%2Cen_US%2Cfr_CA&filter_reviewcomments.q1='
                'contentlocale%3Aeq%3Aen_CA%2Cen_US%2Cfr_CA&filte'
                'r_comments.q1=contentlocale%3Aeq%3Aen_CA%2Cen_US'
                '%2Cfr_CA&limit.q1=4&offset.q1=0&limit_comments.q'
                '1=3&callback=BV._internal.dataHandler0')

        next_review_url = ('http://api.bazaarvoice.com/data/batch.json?passkey'
                '=9u5bt4k1uinp95si5bctgefh2&apiversion=5.5&display'
                'code=11616-en_us&resource.q0=reviews&filter.q0=is'
                'ratingsonly%3Aeq%3Afalse&filter.q0=productid%3Aeq'
                '%3A' + product_token[0] + '_US&filter.q0=contentlo'
                'cale%3Aeq%3Aen_CA%2Cen_US%2Cfr_CA&sort.q0=submis'
                'siontime%3Adesc&stats.q0=reviews&filteredstats.q'
                '0=reviews&include.q0=authors%2Cproducts%2Ccommen'
                'ts&filter_reviews.q0=contentlocale%3Aeq%3Aen_CA%'
                '2Cen_US%2Cfr_CA&filter_reviewcomments.q0=content'
                'locale%3Aeq%3Aen_CA%2Cen_US%2Cfr_CA&filter_comme'
                'nts.q0=contentlocale%3Aeq%3Aen_CA%2Cen_US%2Cfr_'
                'CA&limit.q0=30&offset.q0=4&limit_comments.q0=3&'
                'callback=bv_183_56494')

        content = urllib2.urlopen(first_review_url).read()
        content = self._remove_escape(content)

        review_count_reg = re.compile(r'ReviewText')
        data = review_count_reg.findall(content)
        if len(data) != 0:
            review_count = len(data)

            review_name_reg = \
                re.compile(r'\"UserNickname\":\"(.+?)\",\"Photos\"')
            names = review_name_reg.findall(content)

            rating_reg = re.compile(r'\"Rating\":(\d)')
            ratings = rating_reg.findall(content)

            titles_reg = re.compile(r'\"Title\":\"(.+?)\"')
            titles = titles_reg.findall(content)

            review_content_reg = re.compile('\"ReviewText\":\"(.+?)\"')
            review_contents = review_content_reg.findall(content)

            try :
                content_next = urllib2.urlopen(next_review_url).read()
                content_next = self.__remove_escape(content_next)

                review_count_next_reg = re.compile(r'ReviewText')
                data_next = review_count_next_reg.findall(content_next)
                if len(data_next) != 0:
                    review_count += len(data_next)

                    review_name_next_reg = \
                        re.compile(r'\"UserNickname\":\"(.+?)\",\"Photos\"')
                    names_next = review_name_next_reg.findall(content_next)
                    names += names_next

                    rating_next_reg = re.compile(r'\"Rating\":(\d)')
                    ratings_next = rating_next_reg.findall(content_next)
                    ratings += ratings_next

                    titles_next_reg = re.compile(r'\"Title\":\"(.+?)\"')
                    titles_next = titles_next_reg.findall(content_next)
                    titles += titles_next

                    review_content_next_reg = \
                        re.compile('\"ReviewText\":\"(.+?)\"')
                    review_contents_next = \
                        review_content_next_reg.findall(content_next)
                    review_contents += review_contents_next
            except :
                pass

            for i in range(0, review_count):
                review_sum = review_sum + int(ratings[i])

            review_rating = float(review_sum) / float(review_count)

            for j in range(len(names)):
                review_list.append({'rating':int(ratings[j]),
                    'name':names[j],
                    'title':titles[j],
                    'content':review_contents[j]})
            item['max_review_rating'] = 5
            item['review_count'] = review_count
            item['review_rating'] = review_rating
            item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()