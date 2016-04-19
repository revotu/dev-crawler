# -*- coding: utf-8 -*-
# author: Hu Yishu
import json
import urllib
import urllib2
import scrapy.cmdline
from StringIO import StringIO
from avarsha_spider import AvarshaSpider


_spider_name = 'nathalieschuterman'
class nathalieschutermanSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["nathalieschuterman.com"]
    headers = {
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'no-cache',
        'Connection':'keep-alive',
        'Content-Length':'3599',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
           }

    def __init__(self, *args, **kwargs):
        super(nathalieschutermanSpider, self).__init__(*args, **kwargs)
    def convert_url(self, url):
        idx1 = url.find('#')
        if idx1 != -1:
            url = url[:idx1]
        if 'sv' in url:
            indx1 = url.find('sv')
            indx2 = indx1 + len('sv')
            url = url[:indx1] + 'en' + url[indx2:]
        return url
    def fetch_wish_data(self, url, data, headers):
        req = urllib2.Request(url, urllib.urlencode(data))
        r = urllib2.urlopen(req)
        str = r.read()
        indx1 = str.find('href')
        indx2 = str.find('>', indx1)
        str = str[indx1 + len('href="'):indx2 - 1]
        return str
    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        get_filtered_feed_params = {
            'productId': 0,
        }
#         iddata_xpath = sel.response.body
        iddata = sel.response.body

        flag = iddata.find('.data')
        flag_end = iddata.find('.configure', flag)
        iddata = iddata[flag + len('.data'):flag_end - 1];
        flag = iddata.find('(')
        flag_end = iddata.find(')', flag)

        id_dict = json.loads(iddata[flag + 1:flag_end ])
        id_product = id_dict['products']
        get_filtered_feed_url = self.start_urls[0]
        requests = []
        # len(id_product)
        for index in range(len(id_product)):
            get_filtered_feed_params['productId'] = id_product[index]['id']
            jdata = (self.fetch_wish_data(get_filtered_feed_url,
                 get_filtered_feed_params, self.headers))
            item_url = 'http://www.nathalieschuterman.com' + jdata
            print item_url
            indx = item_url.find('ï')
            if indx != -1:
                item_url = item_url[:indx] + '%C3%AF' + item_url[indx + len('ï'):]
            indx = item_url.find('ä')
            if indx != -1:
                item_url = item_url[:indx] + '%C3%A4' + item_url[indx + len('ä'):]
            item_urls.append(item_url)
            requests.append((scrapy.Request(item_url,
                callback=self.parse_item)))
        return requests


    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@class="product-info c-6"]/div[@class="top"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            data[0] = data[0].replace('\t', '')
            idx0 = data[0].find('\n')
            idx1 = data[0].find('\n', idx0 + 1)
            idx2 = data[0].find('\n', idx1 + 1)
            data[0] = data[0][(idx1 + 1):(idx2 - 1)]
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'nathalie schuterman'

    def _extract_brand_name(self, sel, item):
        brand_name_xpath = '//div[@class="product-info c-6"]/div[@class="top"]/h1/text()'
        data = sel.xpath(brand_name_xpath).extract()
        if len(data) != 0:
            data[0] = data[0].replace('\t', '')
            idx1 = data[0].find('\n')
            idx2 = data[0].find('\r', idx1)
            item['brand_name'] = data[0][(idx1 + 1):idx2 ].strip()


    def _extract_sku(self, sel, item):
        sku_xpath = '//script[@type="text/javascript"]'
        datatotaltext = sel.xpath(sku_xpath).extract()
        datatext = ""
        for index in range(len(datatotaltext)):
            if datatotaltext[index].find('jQuery.noConflict()') != -1:
                datatext = datatotaltext[index]
                break;
        datatext = datatext.replace('"', "")
        idx1 = datatext.find("displayProductId:")
        idx2 = datatext.find(",", idx1)
        data = ""
        if (idx1 != -1 and idx2 != -1):
            data = (datatext[idx1 + len("displayProductId: "):idx2 - 1])
        if len(data) != 0:
            data = data.replace('\'', "")
            item['sku'] = data

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = (
            '//div[@class="product-info c-6"]/div[@class="top"]/div[@class="long-desc"]')
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0]

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):  #######
        # imgs_url_xpath = '//*[@id="product_addtocart_form"]/div[@class="product-essential"]/div[@class="product-img-box"]//@src'
        imgs_url_xpath_f = '//div[@class="product-images c-6"]/div[@class="current"]//li/@data-zoom-src'
        data = sel.xpath(imgs_url_xpath_f).extract()
        base_url = 'http://www.nathalieschuterman.com'
        if len(data) != 0:
            for index in range(len(data)):
                if(data[index].find(base_url) == -1):
                    data[index] = base_url + data[index]
            item['image_urls'] = data




    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        sizes_xpath = '//*[@name="id"]/option/text()'
        data = sel.xpath(sizes_xpath).extract()
        if len(data) != 0:
            data.remove(data[0]);
            for index in range(len(data)):
                data[index] = data[index].replace('\r', '');
                data[index] = data[index].replace('\n', '');
                data[index] = data[index].replace('\t', '');
            item['sizes'] = data


    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="product-info c-6"]/div[@class="top"]/p/span[2]/text()'
        data = sel.xpath(price_xpath).extract()
        # print sel.response.body
        units = ['USD', 'SEK', 'EUR', 'CNY', 'JPY']
        if (len(data) != 0) :
            data[0] = data[0].replace(' ', '')
            data[0] = data[0].replace('\n', '')
            ind = 0
            for index in range(len(units)):
                if data[0].find(units[index]) != -1:
                    ind = index
                    break
            price_number = data[0][0:data[0].find(units[ind]) ].strip()
            item['price'] = self._format_price(units[ind], price_number)
        else:
            self.log('OUT OF STOCK!')




    def _extract_list_price(self, sel, item):
        list_price_xpath = '//div[@class="product-info c-6"]/div[@class="top"]/p/del/text()'
        data = sel.xpath(list_price_xpath).extract()
        price_xpath = '//div[@class="product-info c-6"]/div[@class="top"]/p/span[2]/text()'
        datapri = sel.xpath(price_xpath).extract()
        if len(data) != 0 and len(datapri) != 0:
            data = data[0]
            datapri = datapri[0]
            data = data.replace(' ', '')
            data = data.replace('\n', '')
            datapri = datapri.replace(' ', '')
            datapri = datapri.replace('\n', '')
            units = ['USD', 'SEK', 'EUR', 'CNY', 'JPY']
            ind = 0
            if (len(data) != 0 and data != datapri) :
                for index in range(len(units)):
                    if data.find(units[index]) != -1:
                        ind = index
                        break
                price_number = data[0:data.find(units[ind]) ].strip()
                item['list_price'] = self._format_price(units[ind], price_number)
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
