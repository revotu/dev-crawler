# -*- coding: utf-8 -*-
# author fsp

import base64
import time

import scrapy.cmdline
from scrapy.http import Request
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = 'bergdorfgoodman'

class BergdorfgoodmanSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["bergdorfgoodman.com"]
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36')
    para_dict = {}
    c_id = ''
    total_pages = 0
    if_finished = 0

    def __init__(self, *args, **kwargs):
        super(BergdorfgoodmanSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def convert_url(self, url):
        cid_start_index = url.find('cat')
        cid_end_index = url.find('_', cid_start_index)
        if cid_start_index != -1:
            self.__class__.c_id = url[cid_start_index + len('cat'):cid_end_index]
        else:
            self.__class__.c_id = ''

        enddsr_end_index = url.find('#')
        if enddsr_end_index != -1:
            enddsr_start_index = url.find('?')
            if enddsr_start_index != -1:
                search_index = url[:enddsr_start_index].find('search')
                if search_index != -1:
                    return url[:enddsr_end_index]

                self.__class__.para_dict['endecaDrivenSiloRefinements'] = \
                    url[enddsr_start_index + len('?'):enddsr_end_index]

            para_str = url[url.find('#') + len('#'):]
            para_list = para_str.split('&')
            for line in para_list:
                tmp_list = line.split('=')
                self.__class__.para_dict[tmp_list[0]] = tmp_list[1]

            # process when '#' in start_url
            # post data with url to get item number
            url = 'http://www.bergdorfgoodman.com/category.service'

            # generate post_data
            # format is post_data = post_data_prefix + page_number + post_data_tail
            post_data_prefix = '{"GenericSearchReq":{"pageOffset":'

            post_data_tail = ',"pageSize":"30","refinements":"'
            if 'refinements' in self.__class__.para_dict:
                post_data_tail += self.__class__.para_dict['refinements']
            post_data_tail += '","sort":"'
            if 'sort' in self.__class__.para_dict:
                post_data_tail += self.__class__.para_dict['sort']
            if 'endecaDrivenSiloRefinements' in self.__class__.para_dict:
                post_data_tail += ('","endecaDrivenSiloRefinements":"'
                    + self.__class__.para_dict['endecaDrivenSiloRefinements'])
            post_data_tail += ('","definitionPath":"' + \
                self.__class__.para_dict['definitionPath'] +
                '","userConstrainedResults":"' + \
                self.__class__.para_dict['userConstrainedResults'] +
                '","advancedFilterReqItems":{"StoreLocationFilterReq":[{'
                '"allStoresInput":"false","onlineOnly":""}]},"categoryId":"cat' +
                self.__class__.c_id +
                '","sortByFavorites":false,"isFeaturedSort":false,"prevSort":""}}'
                )

            post_data = post_data_prefix + '0' + post_data_tail
            post_text = 'data=$b64$' + base64.urlsafe_b64encode(post_data) + \
                '&service=getCategoryGrid&timestamp=' + str(int(time.time()))
            return url + '?' + post_text
        else:
            return url

    def make_requests_from_url(self, url):
        # extract key values form url and save
        if url.find('#') != -1:
            new_url = self.convert_url(url)
            return Request(new_url, callback=self.parse, dont_filter=True)
        return Request(url, dont_filter=True)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = 'http://www.bergdorfgoodman.com'
        items_xpath = '//a[@class="prodImgLink"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        requests = []
        if self.__class__.if_finished == 0:
            if self.__class__.c_id == '':
                cat_index = sel.response.url.find('cat')
                cat_end_index = sel.response.url.find('_')
                if cat_index != -1:
                    cat = sel.response.url[cat_index: cat_end_index]
                else:
                    cat = ''

                # icid indicate icid or fromDrawer
                if_search = sel.response.url.find('search')
                if if_search != -1:
                    icid_text = '"endecaDrivenSiloRefinements":"0",'
                else:
                    icid_index = sel.response.url.find('?')
                    if icid_index != -1:
                        icid = sel.response.url[icid_index + len('?') :]
                        icid_text = '"endecaDrivenSiloRefinements":"' + icid + '",'
                    else:
                        icid_text = ''

                max_page_xpath = '//div[@id="epaging"]/div[last()-1]/text()'
                max_page = sel.xpath(max_page_xpath).extract()

                if len(max_page) != 0:
                    requests = []
                    for page in range(int(max_page[0]) - 1):
                        prefix_url = ("http://www.bergdorfgoodman.com/category"
                            ".service?data=")
                        text1 = '{"GenericSearchReq":{"pageOffset":'
                        text2 = (',"pageSize":"30","refinements":"","sort":"",')
                        if_search = sel.response.url.find('search')
                        if if_search != -1:
                            ntt_start_index = sel.response.url.find('Ntt=')
                            ntt_end_index = sel.response.url.find('&', \
                                ntt_start_index)
                            ntt = '","ntt":"' + sel.response.url[ntt_start_index\
                                + len('Ntt='):ntt_end_index] + '"'
                            definition_path = ('"definitionPath":"/nm/commerce'
                                '/pagedef/etemplate/Search"')
                        else:
                            ntt = '"'
                            definition_path = ('"definitionPath":"/nm/commerce'
                                '/pagedef/template/EndecaDriven"')
                        text3 = (',"advancedFilterReqItems":'
                            '{"StoreLocationFilterReq":'
                            '[{"allStoresInput":"false","onlineOnly":""}]},'
                            '"categoryId":"')
                        text4 = ',"sortByFavorites":false,"isFeaturedSort":' + \
                            'false,"prevSort":""}}'
                        text = text1 + str(page + 1) + text2 + icid_text + \
                            definition_path + text3 + cat + ntt + text4
                        tail_url = '&service=getCategoryGrid'
                        tail_url2 = '&service=getFilteredEndecaResult'

                        if if_search != -1:
                            url = prefix_url + '$b64$' + \
                            base64.urlsafe_b64encode(text) + tail_url2
                        else:
                            url = prefix_url + '$b64$' + \
                                base64.urlsafe_b64encode(text) + tail_url

                        list_urls.append(url)
                        requests.append(scrapy.Request(url, callback=self.parse))
                    self.__class__.if_finished = 1
                    return requests
                else:
                    return []
            else:
                # get total pages
                total_pages_start_index = sel.response.body.find('totalPages":')
                total_pages_end_index = sel.response.body.find(',', \
                    total_pages_start_index + len('totalPages":'))
                total_pages = int(sel.response.body[total_pages_start_index + \
                    len('totalPages":'):total_pages_end_index])

                url = 'http://www.bergdorfgoodman.com/category.service'
                # generate post_data
                # format is post_data = post_data_prefix + page_number + post_data_tail
                post_data_prefix = '{"GenericSearchReq":{"pageOffset":'

                post_data_tail = (',"pageSize":"30",'
                    '"refinements":"' + self.__class__.para_dict['refinements']
                    + '","sort":"' + self.__class__.para_dict['sort'])
                if 'endecaDrivenSiloRefinements' in self.__class__.para_dict:
                    post_data_tail += ('","endecaDrivenSiloRefinements":"' +
                        self.__class__.para_dict['endecaDrivenSiloRefinements'])
                post_data_tail += ('","definitionPath":"' + \
                    self.__class__.para_dict['definitionPath'] +
                    '","userConstrainedResults":"' + \
                    self.__class__.para_dict['userConstrainedResults'] +
                    '","advancedFilterReqItems":{"StoreLocationFilterReq":[{'
                    '"allStoresInput":"false","onlineOnly":""}]},'
                    '"categoryId":"cat' + self.__class__.c_id +
                    '","sortByFavorites":false,"isFeaturedSort":false,'
                    '"prevSort":""}}')
                cur_page = 1
                # make requests
                while cur_page < total_pages:
                    post_data = post_data_prefix + str(cur_page) + post_data_tail
                    post_text = 'data=$b64$' + base64.urlsafe_b64encode(\
                        post_data) + '&service=getCategoryGrid&timestamp='\
                        + str(int(time.time()))
                    list_urls.append(url + '?' + post_text)
                    requests.append(scrapy.Request(url + '?' + post_text, \
                        callback=self.parse, dont_filter=True))
                    cur_page += 1
                self.__class__.if_finished = 1
                return requests
        return requests
    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h1[@itemprop="name"]//text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            title = data[len(data) - 1].replace('\t', ' ')\
                .replace('\n', ' ').strip()
            # remove color   after ','
            color_index = title.find(',')
            item['title'] = title[:color_index].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Bergdorfgoodman'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//span[@itemprop="brand"]/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].replace('\t', ' ')\
                .replace('\n', ' ').strip()
        else:
            brand_xpath = '//span[@itemprop="brand"]/text()'
            data = sel.xpath(brand_xpath).extract()
            if len(data) != 0:
                item['brand_name'] = data[0].replace('\t', ' ')\
                .replace('\n', ' ').strip()

    def _extract_sku(self, sel, item):
        pcode_xpath = '//p[@class="GRAY10N OneLinkNoTx"]/text()'
        data = sel.xpath(pcode_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0].replace('\r', ' ').replace('\t', ' ')\
                .replace('\n', ' ').strip()

    def _extract_description(self, sel, item):
        description_xpath = ('//div[@class="cutline"]'
            '//div[@itemprop="description"]/ul |'
            '//div[@class="cutline"]'
            '//div[@itemprop="description"]/h2/ul')
        final_xpath = ('//div[@class="cutline"]'
            '//div[@itemprop="description"]/h2')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            description = data[0].strip()
        else:
            data = sel.xpath(final_xpath).extract()
            description = data[0].strip()
        item['description'] = description

    def _extract_image_urls(self, sel, item):
        images_xpath = '//img[@class="alt-shot"]/@data-zoom-url'
        images_xpath2 = '//img[@itemprop="image"]/@data-zoom-url'
        images = sel.xpath(images_xpath).extract()
        data = sel.xpath(images_xpath2).extract()
        if len(data) != 0:
            if data[0] not in images:
                images.append(data[0])
        if len(images) != 0:
            item['image_urls'] = images

    def _extract_basic_options(self, sel, item):
        content = sel.response.body
        colors = []
        size_list = []
        for line in content.split('\n'):
            if line.find('new product(\'') != -1:
                start_index = line.find('sku')
                start_index = line.find('\',\'', start_index) + len('\',\'')
                end_index = line.find('\',\'', start_index)
                text = line[start_index:end_index]
                # item may not contain size
                # thus, color will be in 'size' place
                if text.isalpha():
                    if text not in colors:
                        colors.append(text)
                    continue
                if text not in size_list:
                    size_list.append(text)
                start_index = end_index + len('\',\'')
                end_index = line.find('\',\'', start_index)
                text = line[start_index:end_index]
                if text not in colors:
                    colors.append(text)
        if len(size_list) != 0:
            item['sizes'] = size_list
        if len(colors) != 0:
            item['colors'] = colors

    def _extract_list_price(self, sel, item):
        price_xpath = '//div[@class="price pos2"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price = data[0].strip()
            item['list_price'] = self._format_price('USD', price[len('$'):])

    def _extract_price(self, sel, item):
        price_xpath = ('//span[@itemprop="price"]/text() | '
            '//div[@itemprop="price"]/text() | //div'
            '[@class="price pos1override"]/text()')
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price = data[0].replace(',', '').replace('\r', '')\
                .replace('\t', '').replace('\n', '').strip()
            item['price'] = self._format_price('USD', price[len('$'):])

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
