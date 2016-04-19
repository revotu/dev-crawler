# -*- coding: utf-8 -*-
'''
Created on 2015/02/07

@author: zhujun
'''


import scrapy.cmdline

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', '6pm'])

if __name__ == '__main__':
    main()
