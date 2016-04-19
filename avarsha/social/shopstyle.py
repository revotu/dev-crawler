'''
Created on 2015/6/18

@author: zhujun
'''

import time
import traceback
import urllib2

from avarsha.dynamo_db import DynamoDB


dynamo = DynamoDB()

for line in file(r'./sources/shopstyle.txt').readlines():
    try:
        splits = line.split('\t')
        url = splits[0].strip()
        like_count = int(splits[4].strip())
        idx = splits[5].strip().find('.')
        crawl_datetime = splits[5].strip()[:idx]
    except:
        print traceback.print_exc()
        continue

    try:
        url = urllib2.urlopen(url).geturl()
    except:
        print traceback.print_exc()

    product_id = dynamo.get_product_id_by_url(url)
    if product_id != None:
        dynamo.save_shopstyle_likes(product_id, like_count, crawl_datetime)
    else:
        print 'URL not exists in products table: %s' % url

    time.sleep(0.5)


if __name__ == '__main__':
    pass
