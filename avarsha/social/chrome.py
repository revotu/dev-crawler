'''
Created on 2015/6/18

@author: zhujun
'''

import traceback
import urllib


from avarsha.dynamo_db import DynamoDB


def url_quote(url):
    try:
        url = url.encode('utf-8')
        return urllib.quote(urllib.unquote(url))
    except:
        print traceback.print_exc()
        return url

segment = 0
total_segments = 100

dynamo = DynamoDB()
results = dynamo.fetch_product_urls(segment, total_segments)
i = 0
for result in results:
    # product_id = result['product_id']
    url = result['url']

    quoted_url = url_quote(url)
    clicks = dynamo.get_chrome_clicks(url)
    if clicks == -1:
        clicks = dynamo.get_chrome_clicks(quoted_url)
    print url, clicks

if __name__ == '__main__':
    pass
