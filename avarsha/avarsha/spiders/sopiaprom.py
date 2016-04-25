# -*- coding: utf-8 -*-
# @author: donglongtu

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'promsbelle'

class SophiapromSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["sophiaprom.com"]
    
    wedding_sku = 709437
    flower_sku = 401042
    dress_sku = 318355

    def __init__(self, *args, **kwargs):
        super(SophiapromSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'http://www.sophiaprom.com'
        items_xpath = '//div[@class="proImgBox"]/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//a[@class="page-next"]/@href'

        # don't need to change this line
        return self._find_nexts_from_list_page(
                sel, base_url, nexts_xpath, list_urls)

    def __remove_escape(self, content):
        content = content.replace('\\\"' , '"')
        content = content.replace('\\n' , '')
        content = content.replace('\\/' , '/')
        return content

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        return
        title_xpath = '//h1[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        item['referer'] = sel.response.request.headers['Referer']

    def _extract_brand_name(self, sel, item):
        return
        if sel.response.url.find('wedding') != -1:
            item['sku'] = str(self.wedding_sku)
            self.wedding_sku += 1
        elif sel.response.url.find('flower') != -1:
            item['sku'] = str(self.flower_sku)
            self.flower_sku += 1
        else:
            item['sku'] = str(self.dress_sku)
            self.dress_sku += 1

    def _extract_sku(self, sel, item):
        sku_xpath = '//div[@class="pro_m"]//em/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['product_id'] = data[0][len('Style:'):]

    def _extract_features(self, sel, item):
        return
        key_xpath = '//ul[@class="content"]/li/span/text()'
        key = sel.xpath(key_xpath).extract()
        val_xpath = '//ul[@class="content"]/li/text()'
        val = sel.xpath(val_xpath).extract()
        if len(key) != 0 and len(val) != 0:
            item['features'] = dict(zip(key,val))
            
    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        return
        img_xpath = '//div[@class="n_thumbImg_item"]/ul/li/img/@data-big-img'
        data = sel.xpath(img_xpath).extract()
        images = []
        if len(data) != 0:
            for index,img in enumerate(data):
                images.append(img + '?index=' + str(index + 1) + '&sku=' + str(item['sku']))
        item['image_urls'] = images

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        return
        price_xpath = '//p[@class="curPrice fl"]/span[@id="unit_price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_list_price(self, sel, item):
        return
        price_xpath = '//span[@class="costPrice"]/span[@id="unit_price"]/text()'
        data = sel.xpath(price_xpath).extract()
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
        return
        sel = Selector(sel.response)
        review_list = []
        nickname_xpath = '//section[@id="review"]//li/p[@class="review_t"]/strong[@class="name"]/text()'
        nickname = sel.xpath(nickname_xpath).extract()
        if len(nickname) != 0:
            content_xpath = '//section[@id="review"]//li/div/text()'
            content = sel.xpath(content_xpath).extract()
            
            for i in range(len(nickname)):
                review_list.append({'name':nickname[i],'content':content[i]})
                
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()