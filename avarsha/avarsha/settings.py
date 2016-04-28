# -*- coding: utf-8 -*-

# Scrapy settings for src project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
# http://doc.scrapy.org/en/latest/topics/settings.html
#

# VERSION = 'RELEASE'
VERSION = 'DEV'

# collection feeds are divided into different spider hosts
NUMBER_OF_HOSTS = 5
CRAWLER_NO = 0

BOT_NAME = 'avarsha'

SPIDER_MODULES = ['avarsha.spiders']
NEWSPIDER_MODULE = 'avarsha.spiders'

#LOG_FILE = 'log.txt'

# Crawl responsibly by identifying yourself
USER_AGENT = 'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Acoo Browser 1.98.744; .NET CLR 3.5.30729)'
#DOWNLOAD_DELAY = 1
DOWNLOAD_DELAY = 0
COOKIES_ENABLED = False

CHROME_ENABLED = True

ITEM_PIPELINES = {
    'avarsha.pipelines.AvarshaImagePipeline': 1,
    'avarsha.pipelines.AvarshaPipeline': 1,
}

# image size
IMAGES_MIN_HEIGHT = 110
IMAGES_MIN_WIDTH = 110
IMAGES_EXPIRES = 90

AWS_ACCESS_KEY_ID = "AKIAJV457HT7IUCL2RHA"
AWS_SECRET_ACCESS_KEY = "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"

if VERSION == 'RELEASE':
    # store images to S3
    IMAGES_STORE = "s3://avarsha/product_images/"
else:
    # store images to local dir
    import os
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    IMAGES_STORE = os.path.join(CUR_DIR, '..', 'images')
