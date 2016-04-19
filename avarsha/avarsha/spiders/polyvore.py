# -*- coding: utf-8 -*-
# @author: wanghaiyi

import urllib
import urllib2

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider


_spider_name = "polyvore"

class PolyvoreSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["polyvore.com"]

    user_agent = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/41.0.2227.0 Safari/537.36')

    def __init__(self, *args, **kwargs):
        super(PolyvoreSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        settings.set('User-Agent', self.user_agent)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.polyvore.com'
        items_xpath = '//div[@class="title"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def _find_items_from_list_page(
            self, sel, base_url, items_xpath, item_urls):
        item_nodes = sel.xpath(items_xpath).extract()
        for i in range(len(item_nodes)):
            item_nodes[i] = item_nodes[i][item_nodes[i].find('/'):]
        requests = []
        for path in item_nodes:
            item_url = path
            if path.find(base_url) == -1:
                item_url = base_url + path
            item_urls.append(item_url)
            requests.append(scrapy.Request(item_url, callback=self.parse_item))
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        requests = []
        sel.response.url
        page_num_url = 2
        grid_idx_num = 60
        idx_search_num = 60
        base_url = 'http://www.polyvore.com/cgi/shop?.in=json&.out=jsonx&request='
        if sel.response.url.find('brand=') != -1:
            brand_name = sel.response.url[sel.response.url.find('brand=') + 6:]
            brand_name = brand_name[:brand_name.find('&')]
        if sel.response.url.find('category_id') == -1 :
            idx1 = sel.response._body
            next_url = ''
            idx1 = idx1.replace('\n' , '')
            while idx1.find('\"jsonx\"') != -1:
                idx_num_tmp = idx1.find('\"jsonx\"')
                idx1 = idx1[idx_num_tmp + 8:]
                idx_num = idx1.find('\"attachNode')
                next_url = idx1[:idx_num - 3]
                next_url = next_url + ',' + '\".passback\":'
            idx1 = sel.response._body
            idx1 = idx1.replace('\n' , '')
            while idx1.find('\"idx_search\"') != -1:
                idx_num_tmp = idx1.find('\"grid_idx_2x2')
                idx1 = idx1[idx_num_tmp:]
                idx_num_tmp = idx1.find('</script>')
                idx3 = idx1[:idx_num_tmp - 1]
                idx1 = idx1[idx_num_tmp:].replace(' ' , '')
                next_url1 = '{' + next_url + '{' + idx3 + '}'
        else:
            idx1 = sel.response._body
            next_url = ''
            idx1 = idx1.replace('\n' , '')
            while idx1.find('\"jsonx\"') != -1:
                idx_num_tmp = idx1.find('\"jsonx\"')
                idx1 = idx1[idx_num_tmp + 8:]
                idx_num = idx1.find('\"attachNode')
                next_url = idx1[:idx_num - 3]
                next_url = next_url + ',' + '\".passback\":'
            idx1 = sel.response._body
            idx1 = idx1.replace('\n' , '')
            while idx1.find('\"idx_search\"') != -1:
                idx_num_tmp = idx1.find('\"grid_idx_2x2')
                idx1 = idx1[idx_num_tmp:]
                idx_num_tmp = idx1.find('</script>')
                idx3 = idx1[:idx_num_tmp - 1]
                idx1 = idx1[idx_num_tmp:].replace(' ' , '')
                next_url1 = '{' + next_url + '{' + idx3 + '}'
        num_tmp = next_url1.find('page\"')
        idx1 = next_url1[:num_tmp + 6]
        tmp_line = next_url1[num_tmp + 6:]
        num_tmp1 = tmp_line.find(',')
        idx2 = tmp_line[num_tmp1:]
        next_url1 = idx1 + str(page_num_url) + idx2
        while True:
            try:
                print next_url1
                next_url2 = next_url1
                if next_url2.find('brand') != -1:
                    tmp_str1 = next_url2[:next_url2.find('brand') + 5]
                    tmp_str1 = urllib.quote(tmp_str1.encode('utf-8'))
                    tmp_str2 = next_url2[next_url2.find('.passback'):]
                    tmp_str2 = urllib.quote(tmp_str2.encode('utf-8'))
                    next_url2 = tmp_str1 + '%22%3A%22' + brand_name + '%22%2C%22' + tmp_str2
                else:
                    next_url2 = urllib.quote(next_url1.encode('utf-8'))
                test_url = base_url + next_url2
                test_url = test_url.replace(' ' , '%')
                content = urllib2.urlopen(test_url).read()
            except Exception as err1:
                break
            else:
                if len(content) <= 250:
                    break
                else:
                    list_urls.append(test_url)
                    requests.append(scrapy.Request(test_url, callback=self.parse))
                    num_tmp = next_url1.find('page\"')
                    idx1 = next_url1[:num_tmp + 6]
                    tmp_line = next_url1[num_tmp + 6:]
                    num_tmp1 = tmp_line.find(',')
                    page_num_url = page_num_url + 1
                    idx2 = tmp_line[num_tmp1:]
                    next_url1 = idx1 + str(page_num_url) + idx2
                    grid_idx_num = grid_idx_num + 60
                    idx_search_num = idx_search_num + 60
                    next_url1 = next_url1[:next_url1.find('grid_idx_2x2') + 14]
                    next_url1 = (next_url1 + str(grid_idx_num) + ',"rand_offset":0,'
                        + '"idx_search":' + str(idx_search_num) + '}}')
        return requests

    def _extract_url(self, sel, item):
        url_xpath = '//*[@id="price_and_link"]/div/a/@href'
        data = sel.xpath(url_xpath).extract()
        if len(data) != 0:
            item['url'] = data[0]

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="box"]/div[@class="bd"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Polyvore'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@id="productStage"]/h1/a[1]/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        data = sel.response.url[sel.response.url.rfind('=') + 1:]
        if len(data) != 0:
            item['sku'] = data

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="tease_container "]/div'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        imgs_xpath = '//meta[@property="twitter:image"]/@content'
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
        price_xpath = '//span[@class="price"]/text()'
        list_price_xpath = '//div[@class="product_info"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$', ''))
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            item['list_price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_list_price(self, sel, item):
        price_xpath = '//span[@class="price"]/text()'
        list_price_xpath = '//div[@class="product_info"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$', ''))
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            item['list_price'] = self._format_price('USD', data[0].replace('$', ''))

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
