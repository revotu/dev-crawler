# -*- coding: utf-8 -*-
# @author: donglongtu

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'dress27'

class Dress27Spider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["27dress.com"]
    
    wedding_sku = 709437
    flower_sku = 401042
    dress_sku = 318355

    def __init__(self, *args, **kwargs):
        super(Dress27Spider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//ul[@class="index_goods_big"]/li/div/a/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//a[@class="next"]/@href'

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
        title_xpath = '//div[@class="mi-content fr"]/div[@class="title"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        item['sku'] = sel.response.url[sel.response.url.find('?sku=') + len('?sku='):]

    def _extract_sku(self, sel, item):
        return
        sku_xpath = '//div[@class="mi-content fr"]/div/h1/span/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['product_id'] = data[0][len('Item Code: '):]

    def _extract_features(self, sel, item):
        return
        key_xpath = '//ul[@class="property"]/li/strong/text()'
        key = sel.xpath(key_xpath).extract()
        val_xpath = '//ul[@class="property"]/li/text()'
        val = sel.xpath(val_xpath).extract()
        if len(key) != 0 and len(val) != 0:
            key = [k.encode('ascii').strip()[:-2] for k in key]
            val = [v.encode('ascii').strip() for v in val if v.encode('ascii').strip()]
            item['features'] = dict(zip(key,val))
            
    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//ul[@class="thumb_list"]/li/a/@rev | //img[@class="goods_pic"]/@src'
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
        price_xpath = '//dd[@class="price-detail"]//strong[@class="shop_price"]/span/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('US$ ', ''))

    def _extract_list_price(self, sel, item):
        return
        price_xpath = '//dd[@class="price-detail"]/del/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['list_price'] = self._format_price('USD', data[0].replace('US$ ', ''))

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
        nickname_xpath = '//div[@id="ECS_COMMENT"]/div[@class="prdrew_content"]/dt/strong/text()'
        nickname = sel.xpath(nickname_xpath).extract()
        if len(nickname) != 0:
            content_xpath = '//div[@id="ECS_COMMENT"]/div[@class="prdrew_content"]/dd/text()'
            content = sel.xpath(content_xpath).extract()
            content = [c.strip() for c in content if c.strip() != 'Hi']
            for i in range(len(nickname)):
                review_list.append({'name':nickname[i].strip()[len('By '):],'content':content[i]})
                
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()