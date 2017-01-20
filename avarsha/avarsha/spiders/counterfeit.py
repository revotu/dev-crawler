# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import urllib2
import smtplib
import os

from urllib2 import Request, urlopen, URLError, HTTPError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider


_spider_name = 'counterfeit'

class CounterfeitSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["counterfeit.technology"]
         
    def load_owner_id(self,owner):
        dir = os.path.dirname(os.path.realpath(__file__))
        file = os.path.join(dir,'..','..','..','database',owner)
        owner_ids = []
        with open(file, 'r') as f:
            owner_ids = [line.rstrip('\n') for line in f]
        return owner_ids
            
    def update_owner_id(self,owner,ids):
        dir = os.path.dirname(os.path.realpath(__file__))
        file = os.path.join(dir,'..','..','..','database',owner)
        with open(file, 'w') as f:
            for id in ids:
                f.write(id + '\n')
    
    def send_email(self,site,add_owner_images_url):
        Me = 'support@dresspirit.com'
        To = ['632624460@qq.com', 'qinyingjie@mingdabeta.com','231130161@qq.com']
        #To = ['632624460@qq.com']
    
        # Create the container (outer) email message.
        msg = MIMEMultipart()
        msg['Subject'] = 'Counterfeit update image urls for %s' % (site)
        # Me == the sender's email address
        # To = the list of all recipients' email addresses
        msg['From'] = Me
        msg['To'] = ",".join(To)
        text = []
        for url in add_owner_images_url:
            text.append('%s' % (url))
        text = "\n".join(text)
        msg.attach(MIMEText(text, 'plain'))
        
        # Send the email via our own SMTP server.
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login('support@dresspirit.com', 'mingDA1234')
        s.sendmail(Me, To, msg.as_string())
        s.quit()
    
    
    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

        base_url = ''
        items_xpath = ''

        return self._find_items_from_list_page(
            sel, base_url, items_xpath, item_urls)

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""

        base_url = ''
        nexts_xpath = ''

        # don't need to change this line
        return self._find_nexts_from_list_page(
            sel, base_url, nexts_xpath, list_urls)

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        pass

    def _extract_store_name(self, sel, item):
        pass

    def _extract_brand_name(self, sel, item):
        pass

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
        dir = sel.response.url[sel.response.url.find('http://')+len('http://'):sel.response.url.find('.counterfeit.technology')]
        load_owner_ids = self.load_owner_id(dir)
        add_owner_images_url = []
        
        img_reg = re.compile(r'"id":"(.+?)","original_url":"(.+?)","thumbnail_url"')
        data = img_reg.findall(sel.response.body)
        
        item['image_urls'] = []
        if len(data) > 0:
            for v in data:
                (id , img_url) = v
                if id not in load_owner_ids:
                    load_owner_ids.append(id)
                    add_owner_images_url.append('http://%s.counterfeit.technology/originals.php?id=%s' %(dir,id))
                    item['image_urls'].append(img_url + '?id=' + id + '&dir=' + dir)
        if len(add_owner_images_url) > 0:
            print add_owner_images_url
            self.send_email(dir,add_owner_images_url)
        self.update_owner_id(dir, load_owner_ids)

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