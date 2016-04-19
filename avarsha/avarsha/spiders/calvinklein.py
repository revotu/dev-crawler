# -*- coding: utf-8 -*-
# author fsp

import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'calvinklein'

class CalvinkleinSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["calvinklein.com"]
    item_number = 0
    if_finished = 0
    url_middle = ''
    url_tail = ''
    url_filters = ''

    def __init__(self, *args, **kwargs):
        super(CalvinkleinSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, list_urls):
        base_url = ''
        nexts_xpath = '//a[@itemprop="name"]/@href'
        if self.__class__.item_number == 0:
            item_number_xpath = ('//span[@class="category_itemSizeNumber'
                ' bold"]/text()')
            data = sel.xpath(item_number_xpath).extract()
            if len(data) != 0:
                self.__class__.item_number = int(data[0].strip())
            return []

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        base_url = ''
        nexts_xpath = ''

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _find_nexts_from_list_page(
        self, sel, base_url, nexts_xpath, list_urls):
        requests = []

        if self.__class__.if_finished == 0:
            if self.__class__.item_number == 0:
                # save parameters:orderBy colors sizes brand in url
                para_dict = {'orderBy':'', 'colors':'', 'sizes':'', 'brand':''}
                para_str = sel.response.url[sel.response.url.find('?') + \
                    len('?'):]
                para_list = para_str.split('&')
                for line in para_list:
                    tmp_list = line.split('=')
                    para_dict[tmp_list[0]] = tmp_list[1]

                # extract parameters:storeId catalogId categoryId parentCategoryName  in url
                url_prefix = 'http://www.calvinklein.com/shop/en/ck/search/'

                first_page_url_xpath = '//a[@data-filter-url]/@data-url'
                data = sel.xpath(first_page_url_xpath).extract()
                if len(data) != 0:
                    first_page_url = url_prefix + data[0].strip()
                    # get storeId catalogId categoryId parentCategoryName
                    store_id_start_index = first_page_url.find('storeId=')
                    end_index = first_page_url.find('&', store_id_start_index)
                    store_id = first_page_url[store_id_start_index\
                        + len('storeId='):end_index]

                    catalog_id_start_index = first_page_url.find('catalogId=')
                    end_index = first_page_url.find('&', catalog_id_start_index)
                    catalog_id = first_page_url[catalog_id_start_index\
                        + len('catalogId='):end_index]

                    category_id_start_index = first_page_url.find('categoryId=')
                    end_index = first_page_url.find('&', category_id_start_index)
                    category_id = first_page_url[category_id_start_index\
                        + len('categoryId='):end_index]

                    pcn_start_index = first_page_url.find('parentCategoryName=')
                    end_index = first_page_url.find('&', pcn_start_index)
                    pcn = first_page_url[pcn_start_index\
                        + len('parentCategoryName='):end_index]

                # open item number page to get total item number
                item_number_url_xpath = '//a[@data-filter-url]/@data-filter-url'
                data = sel.xpath(item_number_url_xpath).extract()
                if len(data) != 0:
                    # generate item_page_url

                    url_middle = 'langId=-1&storeId=' + store_id
                    url_middle += '&catalogId=' + catalog_id
                    url_middle += '&pageSize=60&categoryId=' + category_id
                    url_middle += '&parentCategoryName=' + pcn
                    url_middle += ('&viewAll=Y&showPlusSign='
                        '&showProductGrid=true&pageView=image&beginIndex=')
                    self.__class__.url_middle = url_middle
                    url_tail = ('&showResultsPage=true&metaData='
                        '&isFilter=true&searchType=1000&sType=SimpleSearch'
                        '&filterTerm=&minPrice=&maxPrice=&searchTermScope='
                        '&searchTerm=&resultCatEntryType=&facetParentCategory=')
                    self.__class__.url_tail = url_tail
                    # filters orderBy colors sizes brand in url
                    url_filters = ''
                    if para_dict['orderBy'] != '':
                        url_filters += '&orderBy=' + para_dict['orderBy']
                    if para_dict['colors'] != '':
                        colors = para_dict['colors'].split(',')
                        for color in colors:
                            url_filters += '&facet=cas_f1_ntk_cs%3A%22'\
                                + color + '%22'
                    if para_dict['sizes'] != '':
                        sizes = para_dict['sizes'].split(',')
                        for size in sizes:
                            url_filters += '&facet=cas_f2_ntk_cs%3A%22'\
                                + size + '%22'
                    if para_dict['brand'] != '':
                        url_filters += '&facet=mfName_ntk_cs%3A%22'\
                            + para_dict['brand'] + '%22'
                    self.__class__.url_filters = url_filters
                item_number_url = url_prefix + data[0].strip() + url_filters
                list_urls.append(item_number_url)
                requests.append(scrapy.Request(item_number_url, \
                    callback=self.parse, dont_filter=True))
                return requests
            else:
                # open item page
                url_prefix = 'http://www.calvinklein.com/shop/en/ck/search/'
                begin_index = 0
                while begin_index < self.__class__.item_number:
                    item_page_url = url_prefix + 'CategoryProductDisplayView?' \
                        + self.__class__.url_middle + str(begin_index)\
                        + self.__class__.url_tail + self.__class__.url_filters
                    list_urls.append(item_page_url)
                    requests.append(scrapy.Request(item_page_url, \
                        callback=self.parse, dont_filter=True))
                    begin_index += 30
                self.__class__.if_finished = 1
                return requests
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//span[@itemprop="name"]//text()'
        data = sel.xpath(title_xpath).extract()
        title = ''
        for i in range(len(data)):
            title += ' '.join([data[i]])
        item['title'] = title.strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Calvinklein'

    def _extract_brand_name(self, sel, item):
        store_name_xpath = '//span[@itemprop="name"]/span/text()'
        data = sel.xpath(store_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()

    def _extract_sku(self, sel, item):
        sku_xpath = '//*[@id="sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['sku'] = data[0][len('SKU: #'):]

    def _extract_description(self, sel, item):
        description_xpath = '//div[@class="productBullets"]/ul'
        data = sel.xpath(description_xpath).extract()
        description = ''
        if len(data) != 0:
            description = data[0].replace('\n', '')
        item['description'] = description

    def _extract_image_urls(self, sel, item):
        images_xpath = ('//div[@class="span16 rspn productImageWrapper"]/'
            '@data-zoomimg')
        images = []
        image = sel.xpath(images_xpath).extract()
        if len(image) != 0:
            img_url = image[0]
            main_start_index = img_url.find('main')
            alter_img_url = img_url[:main_start_index]
            alter_img_url += 'alternate1'
            alter_img_url += img_url[main_start_index + len('main'):]
            alter_img_url += '&aci=true'
            images.append(img_url)
            images.append(alter_img_url)
        item['image_urls'] = images

    def _extract_list_price(self, sel, item):
        price_xpath = '//span[@class="price listPrice"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price = data[0].strip()
            item['list_price'] = self._format_price('USD', price[len('$'):])

    def _extract_price(self, sel, item):
        price_xpath = '//span[@class="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            price = data[0].strip()
            item['price'] = 'USD ' + price[len('$'):].strip()
        else:
            price_xpath = '//span[@id="price"]/text()'
            data = sel.xpath(price_xpath).extract()
            if len(data) != 0:
                price = data[0].strip()
                item['price'] = self._format_price('USD', price[len('$'):])

    def _extract_colors(self, sel, item):
        pass
        # TODO:
    def _extract_sizes(self, sel, item):
        pass
        # TODO:

def main():
    scrapy.cmdline.execute(
        argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
