# -*- coding: utf-8 -*-
# @author: fsp

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'bluefly'

class BlueflySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["bluefly.com"]

    def __init__(self, *args, **kwargs):
        super(BlueflySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        base_url = 'http://www.bluefly.com'
        items_xpath = '//div[@class="listProdImage"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'http://www.bluefly.com'
        nexts_xpath = '//div[@class="pageNavigation"]//a/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
                list_url = list_url.replace('^', '%5E')
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//h2[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].replace('\t', ' ')\
                .replace('\n', ' ').strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Bluefly'

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//h1[@class="product-brand"]/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        pcode_xpath = '//span[@class="pdpBulletContentsText"]/text()'
        data = sel.xpath(pcode_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[len(data) - 1].strip()

    def _extract_description(self, sel, item):
        pcode_xpath = '//span[@class="pdpBulletContentsText"]/text()'
        data = sel.xpath(pcode_xpath).extract()
        des = data[0].strip()
        for line in range(len(data) - 1):
            des = '\n'.join([des, data[line + 1].strip('\r').strip('\n')\
                .strip('\t').strip()])
        item['description'] = des

    def _extract_image_urls(self, sel, item):
        images_xpath = '//div[@class="pdpThumbnailContainer"]/a/@rel'
        data = sel.xpath(images_xpath).extract()
        images = []
        if len(data) != 0:
            for content in data:
                image_start_index = content.find('largeimage: \'')
                if image_start_index != -1:
                    image_start_index += len('largeimage: \'')
                    image_end_index = content.find('\'', image_start_index)
                    image = content[image_start_index:image_end_index]
                    image = image.replace('&amp;', '&')
                    x_start_index = image.find('outputx=') + len('outputx=')
                    x_end_index = image.find('&', x_start_index)
                    y_start_index = image.find('outputy=') + len('outputy=')
                    y_end_index = image.find('&', y_start_index)
                    large_image = image[:x_start_index] + '1800'
                    large_image += image[x_end_index:y_start_index] + '2160'
                    large_image += image[y_end_index:]
                    images.append(large_image)
            item['image_urls'] = images

    def _extract_colors(self, sel, item):
        color_xpath = '//div[@class="pdp-label product-variation-label"]/em/text()'
        data = sel.xpath(color_xpath).extract()
        color_list = []
        if len(data) != 0:
            for line in data:
                tmp_list = line.split('/')
                for row in tmp_list:
                    color_list.append(row.strip())
            item['colors'] = color_list

    def _extract_sizes(self, sel, item):
        size_xpath = ('//div[@class="pdpSizeListContainer"]/'
            'span[@class="pdpSizeTile available"]/text()')
        data = sel.xpath(size_xpath).extract()
        size_list = []
        if len(data) != 0:
            for line in data:
                line = line.replace('r', ' ').replace('\n', ' ')\
                    .replace('\t', ' ')
                line = line.strip()
                index = line.find('(')
                if index != -1:
                    size_list.append(line[:index - len(' ')])
                else:
                    size_list.append(line)
            item['sizes'] = size_list

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="pdp-list-price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', (data[0].strip())[len('$'):])

    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="pdp-retail-price"]/text()'
        data = sel.xpath(list_price_xpath).extract()
        if len(data) != 0:
            content = data[0].strip()
            index = content.find('$')
            item['list_price'] = self._format_price('USD', content[index + len('$'):])

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
