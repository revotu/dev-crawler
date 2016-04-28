# -*- coding: utf-8 -*-
# @author: donglongtu

import urllib2

import scrapy.cmdline
from scrapy.selector import Selector

from avarsha_spider import AvarshaSpider


_spider_name = 'weddingtonway'

class WeddingtonwaySpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["weddingtonway.com"]
    
    #wedding_sku = 710933
    flower_sku = 401591
    dress_sku = 326653

    def __init__(self, *args, **kwargs):
        super(WeddingtonwaySpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://www.weddingtonway.com'
        items_xpath = '//div[@class="search-item-container"]//a[@class="search-item-image-link"]/@href'

        # don't need to change this line
        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = '//div[@class="products-pagination-bottom"]//a[@class="products-next-prev-link"][last()]/@href'

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
        title_xpath = '//span[@itemprop="name"]/text()'
        data = sel.xpath(title_xpath).extract()
        if len(data) != 0:
            item['title'] = data[0]

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        if sel.response.url.find('flower') != -1:
            item['sku'] = str(self.flower_sku)
            self.flower_sku += 1
        else:
            item['sku'] = str(self.dress_sku)
            self.dress_sku += 1

    def _extract_sku(self, sel, item):
        item['product_id'] = sel.response.url[sel.response.url.find('?sku=') + len('?sku='):]

    def _extract_features(self, sel, item):
        item['features'] = {}
            
    def _extract_description(self, sel, item):
        description_xpath = '//span[@itemprop="description"]/text()'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            item['description'] = data[0] 

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        img_xpath = '//img[@class="thumb-image"]/@data-original-image-src'
        data = sel.xpath(img_xpath).extract()
        images = []
        if len(data) != 0:
            for index,img in enumerate(data):
                images.append(img + '?index=' + str(index + 1) + '&sku=' + str(item['sku']) +'&dir=weddingtonway')
                
        custom_img_xpath = '//div[@class="product-real-women-photos-container ctrRealWomenPhotos"]/a/@data-modal-dialog-url'  
        data = sel.xpath(custom_img_xpath).extract()
        if(len(data)) != 0:
            for cus_url in data:
                content = urllib2.urlopen('https://www.weddingtonway.com' + cus_url).read()
                content = self.__remove_escape(content)
                sel = Selector(text=content)
                cus_img_xpath = '//img[@class="real-women-modal-image"]/@src'
                cus_img_list = sel.xpath(cus_img_xpath).extract()
                if len(cus_img_list) != 0:
                    index += 1
                    images.append(cus_img_list[0] + '?index=' + str(index + 1) + '&sku=' + str(item['sku']) +'&dir=customimgs')
        
        item['image_urls'] = images

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//span[@class="price-label"]/span[@class="price"]/text() | //div[@class="price"]/span[@itemprop="price"]/text()'
        data = sel.xpath(price_xpath).extract()
        if len(data) != 0:
            item['price'] = self._format_price('USD', data[0].replace('$', ''))

    def _extract_list_price(self, sel, item):
        price_xpath = '//div[@class="price"]/span[@itemprop="price"]/text() | //div[@class="price-tag"]/div/span[@class="original-price"]/text()'
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
        nickname_xpath = '//ul[@id="reviews"]/div[@class="review"]/div[@class="review-details"]/div[@class="name"]/text()'
        nickname = sel.xpath(nickname_xpath).extract()
        if len(nickname) != 0:
            content_xpath = '//ul[@id="reviews"]/div[@class="review"]/div[@class="review-text-container"]/div[@class="review-text"]/text()'
            content = sel.xpath(content_xpath).extract()
            for i in range(len(nickname)):
                review_list.append({'name':nickname[i].strip(),'content':content[i].strip()})
                
        item['review_list'] = review_list

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()