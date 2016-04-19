'''
Created on 2015/6/18

@author: zhujun
'''

import json
import time
import traceback
import urllib
import urllib2

from avarsha.dynamo_db import DynamoDB


def url_quote(url):
    try:
        url = url.encode('utf-8')
        return urllib.quote(urllib.unquote(url))
    except:
        print traceback.print_exc()
        return url

def get_facebook_stats(url):
    fb_api_url = 'https://api.facebook.com/method/links.getStats?urls=%s&format=json' % url
    try:
        f = urllib2.urlopen(fb_api_url)
        jdata = json.loads(f.read())
        if len(jdata) > 0:
            return jdata[0]['share_count'], jdata[0]['like_count'], jdata[0]['comment_count']
        else:
            return 0, 0, 0
    except:
        print 'fetch facebook data meets error.'
        print traceback.print_exc()
        return 0, 0, 0


segment = 0
total_segments = 5

dynamo = DynamoDB()
results = dynamo.fetch_product_urls(segment, total_segments)
i = 0
for result in results:
    product_id = result['product_id']
    url = result['url']

    try:
        url = urllib2.urlopen(url).geturl()
    except:
        print url
        print traceback.print_exc()

    url = url_quote(url)
    share_count, like_count, comment_count = get_facebook_stats(url)

    dynamo.save_facebook_stats(product_id, share_count, like_count, comment_count)

    print 'save facebook stats to dynamo.'

    time.sleep(0.5)


if __name__ == '__main__':
    pass
