'''
Created on 2015/6/18

@author: zhujun
'''

import boto.dynamodb2
from boto.dynamodb2.table import Table
from scrapy.utils.project import get_project_settings

class DynamoDB(object):
    def __init__(self):
        settings = get_project_settings()
        self.conn = boto.dynamodb2.connect_to_region(
            'us-west-1',
            aws_access_key_id=settings['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=settings['AWS_SECRET_ACCESS_KEY'])

    def table(self, table_name):
        return Table(table_name, connection=self.conn)


