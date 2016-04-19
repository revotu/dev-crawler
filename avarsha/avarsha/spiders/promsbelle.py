# -*- coding: utf-8 -*-
# @author: donglongtu

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'promsbelle'

class PromsbelleSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["promsbelle.com"]
    
    wedding_sku = 708669
    flower_sku = 400896
    dress_sku = 313705

    def __init__(self, *args, **kwargs):
        super(PromsbelleSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = '//div[@class="category-products"]/ul[contains(@class,"products-grid")]//a[@class="product-image"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//a[@class="next i-next"]/@href'

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
        title_xpath = '//div[@class="product-name"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
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
        sku_xpath = '//p[@class="product-sku"]/text()'
        data = sel.xpath(sku_xpath).extract()
        if len(data) != 0:
            item['product_id'] = data[0][len('Item Code: '):]

    def _extract_features(self, sel, item):
        th_xpath = '//table[@id="product-attribute-specs-table"]//tbody/tr/th/text()'
        th = sel.xpath(th_xpath).extract()
        td_xpath = '//table[@id="product-attribute-specs-table"]//tbody/tr/td/text()'
        td = sel.xpath(td_xpath).extract()
        if len(th) != 0 and len(td) != 0:
            item['features'] = dict(zip(th,td))
            
    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//a[@class="cloud-zoom-gallery"]/@href'
        data = sel.xpath(img_xpath).extract()
        images = []
        if len(data) != 0:
            for img in data:
                images.append(img + '?sku=' + str(item['sku']))
        item['image_urls'] = images

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@class="product-shop"]/div[@class="price-box"]/p[@class="special-price"]/span[@class="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_list_price(self, sel, item):
        price_xpath = '//div[@class="product-shop"]/div[@class="price-box"]/p[@class="old-price"]/span[@class="price"]/text()'
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
        sel = Selector(sel.response)
        review_list = []
        nickname_xpath = '//div[@class="review-dt"]/span[@class="nickname"]/text()'
        nickname = sel.xpath(nickname_xpath).extract()
        if len(nickname) != 0:
            title_xpath = '//div[@class="review-dd"]/div[@class="title"]/text()'
            title = sel.xpath(title_xpath).extract()
            content_xpath = '//div[@class="review-dd"]//div[@class="value-review-attr"]/text()'
            content = sel.xpath(content_xpath).extract()
            
            for i in range(len(nickname)):
                review_list.append({'name':nickname[i],'title':title[i],'content':content[i]})
                
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()