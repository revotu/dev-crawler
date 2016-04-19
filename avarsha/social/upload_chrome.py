'''
Created on 2015/7/4

@author: zhujun
'''

import os

from avarsha.dynamo_db import DynamoDB


dynamo = DynamoDB()

log_datetime = '1434585600'
for filename in os.listdir(r'./sources'):
    lines = file(os.path.join('./sources', filename)).readlines()
    print filename, len(lines)
    for line in lines:
        splits = line.split(' ')
        url = splits[0].strip()
        clicks = splits[1].strip()
        dynamo.save_chrome_log(url=url, clicks=clicks, datetime=log_datetime)
    print 'finished ', filename

