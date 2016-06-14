# -*- coding: utf-8 -*-
# author: zhujun

import numbers
import re

from lxml import html
from lxml.html import clean

from scrapy import log
from scrapy.item import Item, Field


class ProductItem(Item):
    url = Field()
    title = Field()  # must exist
    store_name = Field()  # string, the name of the website
    brand_name = Field()  # string, the name of the brand
    sku = Field()  # string, the id of the product

    # features is a dict, stores key-value data
    # Example: 'Specifications' in this page are features:
    # http://www.shirleysdress.com/-p700588.html
    features = Field()
    description = Field()
    size_chart = Field()
    color_chart = Field()
    image_urls = Field()  # Used by ImagePipeline

    # Table: product_availabity
    colors = Field()  # list
    sizes = Field()  # list
    stocks = Field()  # default is None, means many stocks

    # Table: product_sales
    price = Field()  # string, must exist
    # string, list_price is the original price of this merchant,
    # but now the store is selling it with the 'price'
    list_price = Field()
    low_price = Field()
    high_price = Field()
    is_free_shipping = Field()  # True or False

    # Table: product_reviews
    # len(review_list) may not equal to review_count, if less reviews are
    # extracted or some reviews are not correctly extracted.
    review_count = Field()  # int
    review_rating = Field()  # float
    max_review_rating = Field()  # float, the max value of rating
    review_list = Field()  # rating, post_time, name, review_title, review_content

    # social data
    chrome_clicks = Field()

    # the following are auto generated
    product_id = Field()  # auto generated from product url
    images = Field()  # auto filled by ImagePipeline
    crawl_datetime = Field()  # when the product is crawled
    updated_datetime = Field()  # if updated since last crawl
    collections = Field()
    
    terms = Field()
    referer = Field()
    email = Field()
    
    dir1 = Field()
    dir2 = Field()

    def normalize_attributes(self):
        normalized_status = True

        normalized_status &= self.__assert_fields_type()
        normalized_status &= self.__assert_prices_format()

        # boto bug, one precision float cannot be saved to dynamodb
        # boto.dynamodb.exceptions.DynamoDBNumberError: BotoClientError:
        # Inexact numeric for `1.4`
        if self.get('review_rating') != None:
            self['review_rating'] = "{:.2f}".format(self.get('review_rating'))

        if self.get('description') != None:
            self['description'] = self.__clean_attrs(self.get('description'))

        return normalized_status

    def __assert_fields_type(self):
        field_type_dict = {'url':basestring,
                           'title':basestring,
                           'store_name':basestring,
                           'brand_name':basestring,
                           'sku':basestring,
                           'features':dict,
                           'description':basestring,
                           'size_chart':basestring,
                           'color_chart':basestring,
                           'image_urls':list,
                           'colors':list,
                           'sizes':list,
                           'stocks':int,
                           'price':basestring,
                           'list_price':basestring,
                           'low_price':basestring,
                           'high_price':basestring,
                           'is_free_shipping':bool,
                           'review_count':int,
                           'review_rating':float,
                           'max_review_rating':int,
                           'review_list':list,
                           'terms':basestring,
                           'referer':basestring,
                           'dir1':basestring,
                           'dir2':basestring,
                           'email':list}

        assert_return = True

        # one level types
        for field, field_type in field_type_dict.items():
            if self.get(field) != None:
                assert_return &= self.__assert_field_type(
                    field, self.get(field), field_type)

        # two level types
        if self.get('colors') != None:
            for color in self.get('colors'):
                assert_return &= self.__assert_field_type(
                    'color element', color, basestring)

        if self.get('sizes') != None:
            for size in self.get('sizes'):
                assert_return &= self.__assert_field_type(
                    'size element', size, basestring)

        # three level types
        if self.get('review_list') != None:
            review_type_dict = {
                'date':basestring,
                'rating':numbers.Number,
                'content':basestring,
                'name':basestring,
                'title':basestring}

            for review in self.get('review_list'):
                assert_return &= self.__assert_field_type(
                    'review', review, dict)
                for field, field_type in review_type_dict.items():
                    if review.get(field) != None:
                        assert_return &= self.__assert_field_type(
                            field, review.get(field), field_type)

        return assert_return

    def __assert_field_type(self, field_name, field_value, expected_field_type):
        if not isinstance(field_value, expected_field_type):
            log.msg('The field [%s] type should be %s!'
                    % (field_name, expected_field_type), log.ERROR)
            return False
        return  True

    def __assert_prices_format(self):
        regex = re.compile(r'^[A-Z]{3}[\s]{1}(\d+|\d{1,3}(,\d{3})*)(\.\d+)?$')
        price_fields = ('price', 'list_price', 'low_price', 'high_price')
        assert_return = True
        for price_field in price_fields:
            if (self.get(price_field) is not None
                and re.match(regex, self.get(price_field)) is None):
                    log.msg(('The format of [%s] is wrong!' % price_field),
                        log.ERROR)
                    assert_return = False
        return assert_return

    def __clean_attrs(self, html_content):
        cleaner = clean.Cleaner(scripts=True,
                                javascript=True,
                                comments=True,
                                safe_attrs_only=True,
                                safe_attrs=[])
        return html.tostring(cleaner.clean_html(html.fromstring(html_content)))

    def __eq__(self, other):
        equal = True
        for field in ProductItem.__dict__.get('fields'):
            if (field == 'crawl_datetime'
                or field == 'updated_datetime'
                or self.get(field) == other.get(field)):
                continue
            else:
                equal = False
        return equal

    def __ne__(self, other):
        if self == other:
            return False
        return True


def main():
    item1 = ProductItem()
    item1['url'] = '100'
    item1.self_assert_type()

if __name__ == '__main__':
    main()
