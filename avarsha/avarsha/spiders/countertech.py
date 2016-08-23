# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json
import urllib2
import smtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider


_spider_name = 'countertech'

class CountertechSpider(AvarshaSpider):
    name = _spider_name
    brand_list = []
    allowed_domains = ["lumendatabase.org"]

    def __init__(self, *args, **kwargs):
        super(CountertechSpider, self).__init__(*args, **kwargs)
        self.load_brand_list()
        
    def load_brand_list(self):
        dir = os.path.dirname(os.path.realpath(__file__))
        file = os.path.join(dir,'..','..','..','countertech')
        with open(file, 'r') as f:
            self.brand_list = [line.rstrip('\n') for line in f]
            f.close()
    def update_brand_list(self):
        dir = os.path.dirname(os.path.realpath(__file__))
        file = os.path.join(dir,'..','..','..','countertech')
        with open(file, 'w') as f:
            for brand in self.brand_list:
                f.write(brand + '\n')
            f.close()

    def send_email(self,brand,url):
        Me = 'support@dresspirit.com'
        To = ['632624460@qq.com', 'donglongtu@163.com']

        # Create the container (outer) email message.
        msg = MIMEMultipart()
        msg['Subject'] = 'Counterfeit.Technology add new Copyright Owners'
        # Me == the sender's email address
        # To = the list of all recipients' email addresses
        msg['From'] = Me
        msg['To'] = ",".join(To)
        text = 'Name : %s ; Link: %s' % (brand, url)
        msg.attach(MIMEText(text, 'plain'))
        
        # Send the email via our own SMTP server.
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login('support@dresspirit.com', 'mingDA1234')
        s.sendmail(Me, To, msg.as_string())
        s.quit()

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = 'https://lumendatabase.org'
        items_xpath = '//ol[@class="results-list"]/li/h3/a/@href'

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = 'https://lumendatabase.org'
        nexts_xpath = '//nav[@class="pagination"]/span[@class="next"]/a/@href'

        nexts = sel.xpath(nexts_xpath).extract()
        requests = []
        for path in nexts:
            list_url = path
            if path.find(base_url) == -1:
                list_url = base_url + path
            page_reg = re.compile(r'page=(.+?)&sender_name')
            data = page_reg.findall(list_url)
            if len(data) > 0:
                page = int(data[0])
                if page > 10:
                    return []
            list_urls.append(list_url)
            request = scrapy.Request(list_url, callback=self.parse)
            requests.append(request)
        return requests

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        pass

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        brand_xpath = '//section[@class="principal secondary hide"]/h6/a/text()'
        data = sel.xpath(brand_xpath).extract()
        if len(data) != 0:
            item['brand_name'] = data[0]
            if item['brand_name'] not in self.brand_list:
                self.brand_list.append(item['brand_name'])
                self.update_brand_list()
                self.send_email(item['brand_name'],sel.response.url)

    def _extract_sku(self, sel, item):
        pass

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        pass

    def _extract_colors(self, sel, item):
        pass

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        pass

    def _extract_list_price(self, sel, item):
        pass

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
    scrapy.cmdline.execute(argv = ['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()