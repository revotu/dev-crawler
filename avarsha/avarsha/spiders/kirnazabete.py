# -*- coding: utf-8 -*-
# author: Hu Yishu
import urllib2
import scrapy.cmdline

from avarsha_spider import AvarshaSpider


_spider_name = 'kirnazabete'
class kirnazabeteSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["kirnazabete.com", "dynamic.sooqr.com"]
    def __init__(self, *args, **kwargs):
        super(kirnazabeteSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        idx = url.find('#')
        if idx != -1:
            searchQuery = ''
            indx1 = url.find('sqr:')
            indx2 = url.find('q', indx1 + len('sqr:'))
            indx3 = url.find('%5B', indx2)
            indx4 = url.find('%5D', indx2)
            if(indx2 != -1):
                searchQuery = '&searchQuery=' + url[(indx3 + len('%5B')):indx4 ];
            indx5 = url.find('f', indx4)
            indx6 = url.find('%5B', indx5)
            indx7 = url.find('%5D', indx5)
            filterQuery = ''
            if indx5 != -1:
                filterQuery = '&filterQuery%5B' + url[(indx5 + 1):indx6] + '%5D%5B%5D=' + url[(indx6 + len('%5B')):indx7]
            baseurl = 'http://dynamic.sooqr.com/suggest/script/?type=suggest'
            filterInitiated = ('&filterInitiated=false&triggerFilter=null&filtersShowAll=false&' + \
            'enableFiltersShowAll=false&filterValuesShowAll=null&securedFilters' + \
            'Hash=false&sortBy=0&offset=0&limit=21&requestIndex=0&locale=en_GB')
            base_url = 'http://www.kirnazabete.com'
            indx1 = url.find(base_url);
            url0 = '&url=' + url[indx1 + len(base_url):idx]
            url0 = url0.replace('/', '%2F')
            tail = '&index=magento%3A531&view=7d50bc81263128f6&account=SQ-100531-1'
            return baseurl + searchQuery + filterQuery + filterInitiated + url0 + tail
        return url

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        requests = []
        if 'http://dynamic.sooqr.com' in self.start_urls[0]:
            resources = sel.response.body
            indx = resources.find('class=\"sqr-button\"')
            while indx != -1:
                indx1 = resources.find('href=\"', indx)
                indx2 = resources.find('"', indx1 + len('href=\"'))
                item_url = resources[(indx1 + len('href=\"')):indx2]
                item_urls.append(item_url)
                requests.append(scrapy.Request(item_url, \
                        callback=self.parse_item))
                indx = resources.find('class=\"sqr-button\"', indx2)
            return requests
        else:
            base_url = 'http://www.kirnazabete.com'
            items_xpath = '//section[@class="category-products"]/ul/li//h2[@class="product-name"]/a[1]/@href'
            # don't need to change this line
            return self._find_items_from_list_page(
                sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        if 'http://dynamic.sooqr.com' in self.start_urls[0]:
            requests = []
            requestIndex = 1
            offset = 21;
            url = self.start_urls[0]
            indx1 = url.find('filterInitiated=')
            url1 = url[:indx1 + len('filterInitiated=')] + 'ture'
            indx2 = url.find('&triggerFilter=null')
            indx3 = url.find('&filterValuesShowAll=null')
            indx4 = url.find('&securedFiltersHash')
            indx5 = url.find('offset=') + len('offset=')
            url2 = url[indx2:indx3] + url[indx4:indx5]
            indx6 = url.find('&limit')
            indx7 = url.find('requestIndex=') + len('requestIndex=')
            url3 = url[indx6:indx7]
            indx8 = url.find('&locale=en_GB')
            url4 = url[indx8:]
            url = url1 + url2 + str(offset) + url3 + str(requestIndex) + url4;
            page = urllib2.urlopen(url).read()
            indx = page.find('class=\\\"sqr-button\\\"')
            while indx != -1:
                list_urls.append(url)
                request = scrapy.Request(url, callback=self.parse)
                requests.append(request)
                offset += 21
                requestIndex += 1
                url = url1 + url2 + str(offset) + url3 + str(requestIndex) + url4;
                page = urllib2.urlopen(url).read()
                indx = page.find('class=\\\"sqr-button\\\"')
            return requests

        else:
            base_url = 'http://www.kirnazabete.com'
            nexts_xpath = '//section[@class="category-products"]/div[@class="toolbar-bottom"]//div[@class="pages"]//a/@href'
            # don't need to change this line
            return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//*[@id="product_addtocart_form"]/div[@class="product-name"]/h2/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0].strip()

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'kirna zabete'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//*[@id="product_addtocart_form"]/div[@class="designer"]/a/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0].strip()


    def _extract_sku(self, sel, item):
        sku_xpath = '//script[@type="text/javascript"]'
        datatotaltext = sel.xpath(sku_xpath).extract()
        datatext = ""
        for index in range(len(datatotaltext)):
            if datatotaltext[index].find('optionsPrice = new Product.OptionsPrice') != -1:
                datatext = datatotaltext[index]
                break;
        datatext = datatext.replace('"', "")
        idx1 = datatext.find("productId:")
        idx2 = datatext.find("priceFormat")
        data = ""
        if (idx1 != -1 and idx2 != -1):
            data = (datatext[idx1 + len("productId:"):idx2 - 2])
        if len(data) != 0:
            item['sku'] = data
        else:
            sku_xpath = '//*[@id="product_addtocart_form"]/div[@class="no-display"]//@value'
            data = sel.xpath(sku_xpath).extract()
            if len(data) != 0:
                item['sku'] = data[0]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = (
            '//*[@id="product_addtocart_form"]/div[@class="description"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            data[0] = data[0].replace("\n", "")
            data[0] = data[0].replace("\t", "")
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):  #######
        # imgs_url_xpath = '//*[@id="product_addtocart_form"]/div[@class="product-essential"]/div[@class="product-img-box"]//@src'
        imgs_url_xpath_f = '//div[@class="more-views"]//li/a/@href'
        data = sel.xpath(imgs_url_xpath_f).extract()
        if len(data) != 0:
            item['image_urls'] = data
        else:
            imgs_url_xpath = '//*[@id="cloudZoom"]/@href'
            data = sel.xpath(imgs_url_xpath).extract()
            if(len(data) != 0):
                item['image_urls'] = data



    def _extract_colors(self, sel, item):
        colors_xpath = '//script[@type="text/javascript"]'
        datatotaltext = sel.xpath(colors_xpath).extract()
        datatext = ""
        for index in range(len(datatotaltext)):
            if datatotaltext[index].find('var spConfig = new Product.Config') != -1:
                datatext = datatotaltext[index]
                break;
        indx0 = datatext.find('"label":"Color"')
        indx1 = datatext.find('"label":"Size"')
        datatext = datatext[indx0:indx1]
        datatext = datatext[datatext.find('options'):]
        datatext = datatext.replace('"', "")
        datatext = datatext.replace('\\', "")
        idx1 = datatext.find("label:")
        idx2 = datatext.find("price")
        numSize = 0
        data = []
        while (idx1 != -1 and idx2 != -1):
            data.append(datatext[idx1 + len("label:"):idx2 - 1])
            numSize = numSize + 1
            datatext = datatext[idx2 + len("price:"):]
            idx1 = datatext.find("label:")
            idx2 = datatext.find("price")
        if len(data) != 0:
            item['colors'] = data


    def _extract_sizes(self, sel, item):
        sizes_xpath = '//script[@type="text/javascript"]'
        datatotaltext = sel.xpath(sizes_xpath).extract()
        datatext = ""
        for index in range(len(datatotaltext)):
            if datatotaltext[index].find('var spConfig = new Product.Config') != -1:
                datatext = datatotaltext[index]
                break;
        indx1 = datatext.find('"label":"Size"')
        datatext = datatext[datatext.find('options', indx1):]
        datatext = datatext.replace('"', "")
        datatext = datatext.replace('\\', "")
        idx1 = datatext.find("label:")
        idx2 = datatext.find("price")
        numSize = 0
        data = []
        while (idx1 != -1 and idx2 != -1):
            data.append(datatext[idx1 + len("label:"):idx2 - 1])
            numSize = numSize + 1
            datatext = datatext[idx2 + len("price:"):]
            idx1 = datatext.find("label:")
            idx2 = datatext.find("price")
        if len(data) != 0:
            item['sizes'] = data


    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//*[@class="regular-price"]/span/text()'
        data = sel.xpath(price_xpath).extract()
        if (len(data) != 0) :
            data[0] = data[0].replace(' ', "")
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD', price_number)
        else:
            price_xpath = '//*[@class="special-price"]/span[@class="price"]/text()'
            data = sel.xpath(price_xpath).extract()
            if (len(data) != 0) :
                data[0] = data[0].replace(' ', "")
                data[0] = data[0].replace('\n', "")
                price_number = data[0][len('$'):].strip()
                item['price'] = self._format_price('USD', price_number)
            else:
                self.log('OUT OF STOCK!')




    def _extract_list_price(self, sel, item):
        price_xpath = '//*[@class="old-price"]/span[@class="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if (len(data) != 0) :
            data[0] = data[0].replace(' ', "")
            data[0] = data[0].replace('\n', "")
            price_number = data[0][len('$'):].strip()
            item['list_price'] = self._format_price('USD', price_number)

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
        pass


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
