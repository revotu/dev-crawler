
# -*- coding: utf-8 -*-
# author: zhujun


import logging
import md5

import os
import json
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display

import scrapy.cmdline
from scrapy.utils.project import get_project_settings

from avarsha_spider import AvarshaSpider
from avarsha.items import ProductItem



selenium_logger = logging.getLogger(
    'selenium.webdriver.remote.remote_connection')
selenium_logger.setLevel(logging.WARNING)

_spider_name = 'google_shopping'

class GoogleShoppingSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["google.com"]

    def __init__(self, *args, **kwargs):
        super(GoogleShoppingSpider, self).__init__(*args, **kwargs)
        self.settings = get_project_settings()
        self.ranking = 0
        self.gs_items = []
        self.WAIT_TIME = self.settings.get("DEFAULT_WAIT_TIME")

    def start_driver(self):
        # Linux use headless mode
        self.display = None
        if os.name == 'posix' and self.settings.get("HEADLESS"):
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()

        self.WAIT_TIME = 30
        options = webdriver.ChromeOptions()
        options.add_argument("--lang=%s" % self.settings.get("DRIVER_LANG"))
        options.add_argument("--start-maximized")

#         proxy = self.settings['PROXIES'].get(self.crawler_ip)
#         if proxy:
#             options.add_argument("--proxy-server=%s" % proxy)

        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.implicitly_wait(self.WAIT_TIME)
        self.logger.info('Start web driver successfully.')

    def close_driver(self):
        if self.display != None:
            self.display.stop()
        self.driver.quit()
        self.logger.info('Goodbye, Google Shopping.')

    def parse(self, response):
#         try:
#             self.start_driver()
#         except Exception, e:
#             self.logger.exception(e)
#             return

        query_url = self.start_urls[0]
        turned_pages = 0
        if self.scrape_products_by_query(query_url, self.turn_pages, turned_pages, self.max_turn_pages) != None:
            self.gs_items = self.__dedup_items_by_product_id(self.gs_items)
            self.logger.debug("%d items scrapyed for Tags: %s" % (len(self.gs_items), str(self.tags)))
            for item in self.gs_items:
                yield item

#         try:
#             self.close_driver()
#         except Exception, e:
#             self.logger.exception(e)
#             return

    def __extract_title(self, parent_element):
        try:
            title = parent_element.find_element_by_xpath('.//div[@class="pspo-content"]/a[@class="pspo-title"] | .//div[@class="pspo-content"]/a[@class="sh-t__title"] | .//a[@class="sh-t__title"]').text
            title = title.replace("\\'", "'")
        except Exception, e:
            self.logger.exception(e)
            return None
        return title

    def __extract_sku(self, parent_element):
        try:
            data_docid = parent_element.get_attribute('data-docid')
        except Exception, e:
            self.logger.exception(e)
            return None
        return data_docid

    def __extract_product_url(self, parent_element, product_meta):
        try:
            data_docid = parent_element.get_attribute('data-docid')
            product_url = product_meta.get(data_docid)[34][6]
            if not product_url.startswith("http"):
                product_url = None
        except Exception, e:
            self.logger.error("Extract product url.")
            self.logger.exception(e)
            return None
        return product_url

    def __extract_description(self, parent_element):
        try:
            if parent_element.get_attribute('outerHTML').find("sh-ds__full-txt") == -1:
                self.logger.debug("No description extracted.")
                return None
            description = parent_element.find_element_by_xpath('.//span[@class="sh-ds__full"]/span[@class="sh-ds__full-txt"]').get_attribute('outerHTML')
            description = description.encode('utf-8')
        except Exception, e:
            self.logger.debug("No description extracted.")
            self.logger.exception(e)
            return None
        return description

    def __extract_price(self, parent_element):
        try:
            # price = parent_element.find_element_by_xpath('.//div[@class="pspo-ol-price pspo-price-with-merchant"]/b').text
            price = parent_element.find_element_by_xpath('.//div[@class="psgextra"]//span[@class="price"]/b').text
            if price.startswith('$'):
                price = self._format_price("USD", price.replace('$', ''))
            else:
                return None
        except Exception, e:
            self.logger.exception(e)
            return None
        return price

    def __download_images(self, image_urls):
        for image_url in image_urls:
            current_window = self.driver.current_window_handle
            self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
            self.driver.switch_to_window(self.driver.window_handles[1])

            self.driver.get(image_url)

            self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 's')

            self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
            self.driver.switch_to_window(current_window)

    def __extract_image_urls(self, parent_element, product_meta):
        try:
            outer_html = parent_element.get_attribute('outerHTML')
            if outer_html.find("sh-mo__old-media-options sh-mo__media-options") != -1:
                zoom_img_element = self.driver.find_element_by_xpath('//div[@class="pspo-popout pspo-gpop"][not(contains(@style, "display: none"))]//div[@class="sh-mo__old-media-options sh-mo__media-options"]//div[@class="sh-mo__image-hover sh-th__container sh-th__center-container"] | //div[@class="pspo-popout pspo-gpop"][not(contains(@style, "display: none"))]//div[@class="_-bb sh-mo__media-options"]//a[@class="_-bc sh-mo__zoom"]')
                # zoom_img_element = self.driver.find_element_by_xpath('//div[@class="pspo-popout pspo-gpop"][not(contains(@style, "display: none"))]//div[@class="sh-mo__old-media-options sh-mo__media-options"]')
            else:
                zoom_img_element = None
        except Exception, e:
            self.logger.exception(e)
            zoom_img_element = None

        try:
            if zoom_img_element != None:
                actions = ActionChains(self.driver)
                actions.click(zoom_img_element)
                actions.perform()

                wait = WebDriverWait(self.driver, self.WAIT_TIME)
                overlay_element = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="sg-resultoverlay__overlay"][not(contains(@style, "display: none"))] | //div[@class="sh-rso__overlay-inner sh-rso__media_viewer_overlay"][not(contains(@style, "display: none"))]')))

                img_url = overlay_element.find_element_by_xpath('.//div[@class="sg-m-i__image-zoom-container"]/img').get_attribute('src')

                # close the pop window
                close_element = overlay_element.find_element_by_xpath('.//div/a[@class="sg-resultoverlay__close"] | .//div/a[@class="sh-rso__close"]')
                close_element.click()

                self.logger.debug("Got a large image URL.")
                return [img_url]
        except Exception, e:
            self.logger.debug("Fetch large image meets exception.")
            self.logger.exception(e)
            img_url = None

        try:
            img_url = parent_element.find_element_by_xpath('.//div[@class="sh-th__container sh-th__center-container"]/img | .//a[@class="sh-si__image"]/div/img').get_attribute('src')
        except Exception, e:
            self.logger.exception(e)
            return None
        self.logger.debug("Got a small image URL.")
        return [img_url]

    def __extract_product_meta_from_page_source(self, page_source):
        start_tag = '{"l":[1],"r":'
        end_tag = '},"st":{}'

        start_index = page_source.find(start_tag)
        if start_index == -1:
            return None
        start_index = start_index + len(start_tag)
        end_index = page_source.find(end_tag, start_index)
        meta_text = page_source[start_index:end_index]
        product_meta = json.loads(meta_text)
        return product_meta


    def _generate_product_id(self, item):
        if item.get('url') is None:
            self.logger.warning('URL not scrapyed.')
            return None
        id_feed_string = item['url']
        m = md5.new()
        m.update(id_feed_string)
        return m.hexdigest()[:16]

    def _save_product_id(self, item):
        product_id = self._generate_product_id(item)
        if product_id != None:
            item['product_id'] = self._generate_product_id(item)

    def __dedup_items_by_product_id(self, item_list):
        seen = set()
        seen_add = seen.add
        return [x for x in item_list if not (x.get("product_id") in seen or seen_add(x.get("product_id")))]

    def scrape_products_by_query(self, query_url, turn_pages=False, turned_pages=0, max_turn_pages=1):
        if turned_pages == 0:
            self.driver.get(query_url)

        try:
            wait = WebDriverWait(self.driver, self.WAIT_TIME)
            product_elements = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//div[@class="psgicont"]')))
        except:
            self.logger.error('Wait timeout.')
            return None

        product_meta = self.__extract_product_meta_from_page_source(self.driver.page_source)
        if product_meta is None:
            self.logger.error("No product meta found.")
            return None
        # print json.dumps(product_meta, sort_keys=True, indent=4, separators=(',', ': '))

        for product_element in product_elements:
            try:
                product_element.click()

                wait = WebDriverWait(self.driver, self.WAIT_TIME)
                wait.until(EC.element_to_be_clickable(
                           (By.XPATH, '//div[@class="pspo-popout pspo-gpop"][not(contains(@style, "display: none"))]//div[@class="gko-a-lbl"]')))

                pop_element = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="pspo-popout pspo-gpop"][not(contains(@style, "display: none"))]')))
            except Exception, e:
                self.logger.exception(e)
                continue

            time.sleep(self.settings["TIMEOUT_BETWEEN_PRODUCTS"])

            item = ProductItem()

            sku = self.__extract_sku(pop_element)
            if sku != None:
                item['sku'] = sku

            product_url = self.__extract_product_url(pop_element, product_meta)
            if product_url != None:
                item['url'] = product_url

            title = self.__extract_title(pop_element)
            if title != None:
                item['title'] = title

            description = self.__extract_description(pop_element)
            if description != None:
                item['description'] = description

            # price = self.__extract_price(pop_element)
            price = self.__extract_price(product_element)
            if price != None:
                item['price'] = price

            image_urls = self.__extract_image_urls(pop_element, product_meta)
            if image_urls != None:
                item['image_urls'] = image_urls

            item['spider'] = self.name
            self._save_product_id(item)
            item['rank'] = self.ranking
            self.ranking += 1
            item['tags'] = self.tags

            # yield item
            self.logger.debug(item)
            self.gs_items.append(item)

        if turn_pages and turned_pages + 1 < max_turn_pages:
            try:
                next_element = self.driver.find_element_by_xpath('//td[@class="b navend"]/a[@id="pnnext"]')
                next_element.click()
            except Exception, e:
                self.logger.exception(e)
                self.logger.debug("Not found next page element.")
                return self.gs_items

            time.sleep(self.settings["TIMEOUT_BETWEEN_PAGES"])

            query_url = self.driver.current_url
            self.logger.debug("Navigate to next page: " + query_url)
            turned_pages += 1
            return self.scrape_products_by_query(query_url, turn_pages, turned_pages, max_turn_pages)
        else:
            return self.gs_items


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()