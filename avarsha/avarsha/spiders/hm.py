# -*- coding: utf-8 -*-
# @author: wanghaiyi

import urllib2

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider



_spider_name = "hm"

class HmSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["hm.com"]


    user_agent = ('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like '
        'Gecko) Chrome/41.0.2228.0 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(HmSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def set_crawler(self, crawler):
        super(HmSpider, self).set_crawler(crawler)
        crawler.settings.set('User-Agent', self.user_agent)

    def convert_url(self, url):
        if url.find('search') == -1:
            if url.find('#') != -1:
                url_tmp = url[:url.find('?') + 1]
                url_tmp2 = url[url.find('#') + 1:]
                url = url_tmp + '&' + url_tmp2
        else:
            search_word = url[url.find('q=') + 2:]
            first_num = 91
            last_num = 180
            search_url1 = 'http://www.hm.com/us/ajaxSearch?term='
            url = (search_url1 + search_word + '&first=' + str(first_num)
                + '&last=' + str(last_num) + '&order=relevance_desc')
        return url


    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        requests = []
        if sel.response.url.find('ajaxSearch') == -1:
            base_url = ''
            items_xpath = '//li[@class="has-secondary-image"]/div/a/@href'
            item_nodes = sel.xpath(items_xpath).extract()
            for path in item_nodes:
                item_url = path
                if path.find(base_url) == -1:
                    item_url = base_url + path
                item_urls.append(item_url)
                request = scrapy.Request(item_url, callback=self.parse_item)
                requests.append(request)
        else:
            content = sel.response.body
            content = content.replace('\n' , '')
            while content.find('articleUrl') != -1:
                idx_num_tmp = content.find('articleUrl')
                idx1 = content[idx_num_tmp + 13:]
                content = content[idx_num_tmp + 13:]
                item_url_tmp = idx1[:idx1.find('","')]
                item_urls.append(item_url_tmp)
                request = scrapy.Request(item_url_tmp, callback=self.parse_item)
                requests.append(request)
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        requests = []
        if sel.response.url.find('ajaxSearch') == -1:
            base_url = self.start_urls[0][:self.start_urls[0].rfind('?')]
            nexts_xpath = '//ul[@class="pages bottom"]/li/a/@href'
            nexts = sel.xpath(nexts_xpath).extract()
            if len(nexts) == 0:
                nexts_xpath = '//section[@class="hm-pager"]/a[@class="NEXT "]/@href'
                nexts = sel.xpath(nexts_xpath).extract()

            for path in nexts:
                list_url = path
                if path.find(base_url) == -1:
                    list_url = base_url + path
                list_urls.append(list_url)
                request = scrapy.Request(list_url, callback=self.parse)
                requests.append(request)
        else:
            first_num = 1
            last_num = 90
            search_url1 = 'http://www.hm.com/us/ajaxSearch?term='
            search_url2 = sel.response.url[sel.response.url.find('term=') + 5\
                :sel.response.url.find('first') - 1]
            search_url = (search_url1 + search_url2 + '&first=' + str(first_num)
                + '&last=' + str(last_num) + '&order=relevance_desc')
            while True:
                try:
                    req = urllib2.Request(search_url)
                    req.add_header('User-Agent', self.user_agent)
                    content = urllib2.urlopen(req).read()
                except:
                    break
                else:
                    if len(content) <= 30000:
                        break
                    else:
                        print search_url
                        list_urls.append(search_url)
                        requests.append(scrapy.Request(search_url, callback=self.parse))
                        first_num += 90
                        last_num += 90
                        search_url = (search_url1 + search_url2 + '&first=' +
                            str(first_num) + '&last=' + str(last_num)
                                + '&order=relevance_desc')
        return requests

    def __remove_escape(self, content):
        content = content.replace('\\\"' , '"')
        content = content.replace('\\n' , '')
        content = content.replace('\\/' , '/')
        return content

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//ul[@class="breadcrumbs"]/li/strong/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Hm'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Hm'

    def _extract_sku(self, sel, item):
        data = sel.response.url[sel.response.url.rfind('=') + 1:]
        if len(data) != 0:
            item['sku'] = data

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="description"]/p'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0].strip()

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = ('//div[@id="images"]/div/img/@src | '
            '//div[@class="thumbs"]/ul/li/a/@href')
        data = sel.xpath(imgs_xpath).extract()
        for i in range(len(data)):
            data[i] = 'https:' + data[i]
        if len(data) != 0:
            item['image_urls'] = data

    def _extract_colors(self, sel, item):
        color_xpath = '//ul[@id="options-articles"]/li/a/span/text()'
        data = sel.xpath(color_xpath).extract()
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        size_list_xpath = ('//li[@class="width1"]/a/span/text() | '
            '//li[@class="width2"]/a/span/text()')
        data = sel.xpath(size_list_xpath).extract()
        if len(data) != 0:
            item['sizes'] = data

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@class="price"]/span/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_list_price(self, sel, item):
        price_xpath = '//span[@class="price"]/span/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            if len(data) == 2:
                item['list_price'] = self._format_price('USD', data[1].replace('$', ''))

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
        pass

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
