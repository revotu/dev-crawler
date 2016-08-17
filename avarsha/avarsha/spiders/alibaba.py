# -*- coding: utf-8 -*-
# author: donlongtu

import scrapy.cmdline
import re
import json
import urllib2
import os

from scrapy.selector import Selector
from avarsha_spider import AvarshaSpider


_spider_name = 'Alibaba'

class AlibabaSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["1688.com"]
    map = { 'https://moffichina.1688.com/?spm=a261y.7663282.0.0.NLm4Tg' : 'b2b-1639203796',
            'https://shop1414600960557.1688.com/?spm=a261y.7663282.0.0.EEeVYT' : 'b2b-2281787162',
            'https://disiboli.1688.com/?spm=a261y.7663282.0.0.6rJNhx' : 'b2b-2566354365ii9gg',
            'https://yazefs.1688.com/?spm=a261y.7663282.0.0.OrFs7L' : 'b2b-1776893553',
            'https://nmtfashion.1688.com/?spm=a261y.7663282.0.0.rmQEmS' : 'b2b-2809683073ce4a8',
            'https://463426.1688.com/?spm=a261y.7663282.0.0.3UABwj' : 'b2b-2115717855',
            'https://shop1438966412150.1688.com/?spm=a261y.7663282.0.0.M47i5u' : 'b2b-2614511269d7163',
            'https://richcoco.1688.com/?spm=a261y.7663282.0.0.cy4ZFr' : 'b2b-25968419368de80',
            'https://bootyjeans.1688.com/?spm=a261y.7663282.0.0.VV05np' : 'b2b-2103152564',
            'https://mengtuibian.1688.com/?spm=a261y.7663282.0.0.yJ11be' : 'b2b-2486134593',
            'https://shandafz.1688.com/?spm=a261y.7663282.0.0.Wdsc5p' : 'b2b-1880204240',
            'https://yigelila.1688.com/?spm=a261y.7663282.0.0.YWBTTP' : 'yigelila',
            'https://glie88.1688.com/?spm=a261y.7663282.0.0.6AsJtH' : 'b2b-2638178200ecfdf',
            'https://glfs99.1688.com/?spm=a261y.7663282.0.0.Ieeain' : 'b2b-290102634905802',
            'https://ivy1688.1688.com/?spm=a261y.7663282.0.0.5Bf4UC' : 'b2b-2549502782qmphp',
            'https://wuyugongzuoshi.1688.com/?spm=a261y.7663282.0.0.ByKAjh' : 'b2b-2810974432fbe82',
            'https://shop1457973990418.1688.com/?spm=a261y.7663282.0.0.nJcYLA' : 'b2b-2822595283bfb3e',
            'https://dxyuanchuang.1688.com/?spm=a261y.7663282.0.0.j660yh' : 'b2b-2194728603',
            'https://mad925.1688.com/?spm=a261y.7663282.0.0.Ghq1Qv' : 'b2b-26558214675077f',
            'https://yufei1910.1688.com/?spm=a261y.7663282.0.0.l2JIlJ' : 'b2b-284177329916dbc',
            'https://domeya.1688.com/?spm=a261y.7663282.0.0.iRq8C5' : 'domeya',
            'https://shop1466070500082.1688.com/?spm=a261y.7663282.0.0.ghDUkS' : 'b2b-2917787387d973e',
            'https://shop1389977563097.1688.com/?spm=a261y.7663282.0.0.3OewOW' : 'b2b-1928758450',
            'https://ninethink.1688.com/?spm=a261y.7663282.0.0.d96QZV' : 'gdeas',
            'https://lztlylzt.1688.com/?spm=a261y.7663282.0.0.71J83c' : 'b2b-268862665902e6c',
            'https://taianniuzai.1688.com/?spm=a261y.7663282.0.0.BhM6AM' : 'b2b-1883071589',
            'https://shop1382547243040.1688.com/?spm=a261y.7663282.0.0.HENC6h' : 'b2b-1731792781',
            'https://shop1455814290590.1688.com/?spm=a261y.7663282.0.0.wALm7U' : 'b2b-28085289929d5c7',
            'https://shop1369242245680.1688.com/?spm=a261y.7663282.0.0.viaBHN' : 'b2b-1695886088',
            'https://gzll4321.1688.com/?spm=a261y.7663282.0.0.w9lfaP' : 'b2b-1759335148',
            'https://styleshop.1688.com/?spm=a261y.7663282.0.0.lnVQIP' : 'b2b-282196755662565',
            'https://shop1457973990418.1688.com/?spm=a261y.7663282.0.0.Ind8MF' : 'b2b-2822595283bfb3e',
            'https://norakids.1688.com/?spm=a261y.7663282.0.0.UCJ7Sg' : 'norakids',
            'https://shop1457369874969.1688.com/?spm=a261y.7663282.0.0.POMK8Z' : 'b2b-2823592542cc87a',
            'https://tianyigarment888.1688.com/?spm=a261y.7663282.0.0.oHgtuT' : 'b2b-2383046432',
            'https://inpluslady.1688.com/?spm=a261y.7663282.0.0.OD1FGT' : 'pfjcn',
            'https://zhizaolian.1688.com/?spm=a261y.7663282.0.0.T3iEjZ' : 'b2b-1110486173',
            'https://tailorh.1688.com/?spm=a261y.7663282.0.0.EEbcD7' : 'b2b-2027277550',
            'https://shop1443545626425.1688.com/?spm=a261y.7663282.0.0.jqeeJa' : 'b2b-26537079770a801',
            'https://shop1386602621902.1688.com/?spm=a261y.7663282.0.0.andIS1' : 'b2b-1923237305',
            'https://boran2015.1688.com/?spm=a261y.7663282.0.0.4KIoh6' : 'b2b-2435791211',
            'https://shop1387472153459.1688.com/?spm=a261y.7663282.0.0.buHFt6' : 'b2b-1928440648',
            'https://nantaoli.1688.com/?spm=a261y.7663282.0.0.sVppGr' : 'nantaoli',
            'https://shop1456159917797.1688.com/?spm=a261y.7663282.0.0.vfeCww' : 'b2b-2809426117c8b06',
            'https://fengshangmy.1688.com/?spm=a261y.7663282.0.0.BtzrEw' : 'b2b-28209010814df34',
            'https://shop1468515342367.1688.com/?spm=a261y.7663282.0.0.gRHmaI' : 'b2b-2922832966f09a4',
            'https://tailring2013.1688.com/?spm=a261y.7663282.0.0.T0HqXh' : 'oyjh1986',
            'https://szmdfs.1688.com/?spm=a261y.7663282.0.0.eOE99w' : 'szmdfs',
            'https://shop1411663726915.1688.com/?spm=a261y.7663282.0.0.zOKkMU' : 'b2b-2245528605',
            'https://jzsecret.1688.com/?spm=a261y.7663282.0.0.jkP1ph' : 'b2b-285103836018d90',
            'https://sunbay.1688.com/?spm=a261y.7663282.0.0.QCqtzu' : 'b2b-2720370231febc5',
            'https://praguefactory.1688.com/?spm=a261y.7663282.0.0.Tic5sM' : 'praguefactory',
            'https://qiaocode.1688.com/?spm=a261y.7663282.0.0.hVZkMQ' : 'b2b-2126806156',
            'https://shop1418648091957.1688.com/?spm=a261y.7663282.0.0.zXiaqU' : 'b2b-2292067960',
            'https://esisto.1688.com/?spm=a261y.7663282.0.0.FaTXNy' : 'b2b-2466413677',
            'https://shop1430413726436.1688.com/?spm=a261y.7663282.0.0.uFinM9' : 'b2b-2519449306',
            'https://shop1462467358748.1688.com/?spm=a261y.7663282.0.0.7NsFMb' : 'b2b-28365970970760b',
            'https://uperfeet.1688.com/?spm=a261y.7663282.0.0.2xFoVS' : 'b2b-1893739209',
            'https://threasa365.1688.com/?spm=a261y.7663282.0.0.jJjMa2' : 'threasa365',
            'https://yikexin.1688.com/?spm=a261y.7663282.0.0.w2vDYi' : 'b2b-2862721619f1fcc',
            'https://shop1356491221946.1688.com/?spm=a261y.7663282.0.0.d4492d' : 'niuniu2218150100',
            'https://room404fashion.1688.com/?spm=a261y.7663282.0.0.OO8gHg' : 'b2b-2507004323',
            'https://shop1457800611660.1688.com/?spm=a261y.7663282.0.0.hthLLg' : 'b2b-282196283310a8e',
            'https://aitaofs.1688.com/?spm=a261y.7663282.0.0.koyHru' : 'b2b-2783396329ef6ac',
            'https://shop1417020263291.1688.com/?spm=a261y.7663282.0.0.21Pxpz' : 'b2b-2335675512',
            'https://shop1458061328757.1688.com/?spm=a261y.7663282.0.0.hcbYUt' : 'b2b-283270330984158',
            'https://shop1460286234372.1688.com/?spm=a261y.7663282.0.0.anVa1H' : 'b2b-2159943550',
            'https://shop1433565999145.1688.com/?spm=a261y.7663282.0.0.soIK8l' : 'b2b-2557991032vyaxi',
            'https://nellbang.1688.com/?spm=a261y.7663282.0.0.wiue1z' : 'b2b-284906314902e42',
            'https://ivy1688.1688.com/?spm=a261y.7663282.0.0.pf4OWl' : 'b2b-2549502782qmphp',
            'https://jieranbutong2010.1688.com/?spm=a261y.7663282.0.0.KlkhFk' : 'jieranbutong2010',
            'https://15612999888.1688.com/?spm=a261y.7663282.0.0.0i7HJx' : 'b2b-2034918831',
            'https://8666666.1688.com/?spm=a261y.7663282.0.0.qNeVx4' : 'b2b-1651364747',
            'https://shop1459492670165.1688.com/?spm=a261y.7663282.0.0.ug4Zpm' : 'b2b-28507118115a868',
            'https://zhenlepf.1688.com/?spm=a261y.7663282.0.0.Bkw8dY' : 'b2b-2086936611',
            'https://szoukasi.1688.com/?spm=a261y.7663282.0.0.0Aued9' : 'gzposh1535',
            'https://txsikya.1688.com/?spm=a261y.7663282.0.0.I67MmA' : 'b2b-1707486235',
            'https://nellbang.1688.com/?spm=a261y.7663282.0.0.Mur2pJ' : 'b2b-284906314902e42',
            'https://diddistudio.1688.com/?spm=a261y.7663282.0.0.EsYYyh' : 'b2b-2225166323',
            'https://huihua163.1688.com/?spm=a261y.7663282.0.0.AYY1MD' : 'b2b-2694211336ed9d2',
            'https://bhknit.1688.com/?spm=a261y.7663282.0.0.bXqSqB' : 'b2b-2514107316',
            'https://woolchina.1688.com/?spm=a261y.7663282.0.0.i7ohJ5' : 'b2b-1993634559',
            'https://txsikya.1688.com/?spm=a261y.7663282.0.0.7bLEOA' : 'b2b-1707486235',
            'https://vinnie.1688.com/?spm=a261y.7663282.0.0.zyutgB' : 'b2b-2680926720422e9',
            'https://yiluqizhiyichang.1688.com/?spm=a261y.7663282.0.0.DnieNB' : 'b2b-2758143496d6198',
            'https://shop1433524250700.1688.com/?spm=a261y.7663282.0.0.IuWEZf' : 'b2b-2556112733w2zvg',
            'https://ruiqiuer888.1688.com/?spm=a261y.7663282.0.0.Ba8vYG' : 'b2b-2202436190',
            'https://shop1463418018875.1688.com/?spm=a261y.7663282.0.0.eLp8fa' : 'b2b-2883379302a0dc5',
            'https://mymissonforyoung.1688.com/?spm=a261y.7663282.0.0.jXsrjT' : 'b2b-2298211704',
            'https://nnlyt.1688.com/?spm=a261y.7663282.0.0.VwQ1XP' : 'nnlyt',
            'https://xinlio.1688.com/?spm=a261y.7663282.0.0.Ww02g4' : 'b2b-2468835071',
            'https://shop1430758528047.1688.com/?spm=a261y.7663282.0.0.fdKlQD' : 'b2b-2517897838',
            'https://daizi520.1688.com/?spm=a261y.7663282.0.0.UhfS3U' : 'b2b-2517897838',
            'https://leatherhandmade.1688.com/?spm=a261y.7663282.0.0.vDQB14' : 'b2b-1651394235',
            'https://shop1438361572335.1688.com/?spm=a261y.7663282.0.0.c6ofxI' : 'b2b-260036269585298',
            'https://shop1395334679295.1688.com/?spm=a261y.7663282.0.0.26RiSA' : 'b2b-2026477170',
            'https://shop1450803158402.1688.com/?spm=a261y.7663282.0.0.dh2hiz' : 'b2b-2754553261e8491',
            'https://shop1405183957228.1688.com/?spm=a261y.7663282.0.0.oJJMm6' : 'b2b-1816235817',
            'https://shop1459528886818.1688.com/?spm=a261y.7663282.0.0.SphE0B' : 'b2b-2847846249efc59',
            'https://colloyesbikini.1688.com/?spm=a261y.7663282.0.0.behzed' : 'b2b-2215885161',
            'https://shop1438855592036.1688.com/?spm=a261y.7663282.0.0.Lgtlyo' : 'b2b-2600035698a738d',
            'https://shop1430066700054.1688.com/?spm=a261y.7663282.0.0.tEIrQJ' : 'b2b-2494874495',
            'https://iglamshop.1688.com/?spm=a261y.7663282.0.0.PwB6tC' : 'b2b-270640571843ed8',
            'https://shop1382028923435.1688.com/?spm=a261y.7663282.0.0.1B2yW8' : 'b2b-1851606549'}

    def __init__(self, *args, **kwargs):
        super(AlibabaSpider, self).__init__(*args, **kwargs)

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""

#         member_id_reg = re.compile(r'member_id:"(.+?)"')
#         data = member_id_reg.findall(sel.response.body)
#         if len(data) == 0:
#             return []
#         member_id = data[0]
        if sel.response.url in self.map:
            member_id = self.map[sel.response.url]
        else:
            return []
        
        pageIndex = 1
        sku = 1
        requests = []
        while True:
            list_url = 'http://m.1688.com/winport/asyncView?memberId=' + str(member_id) + '&pageIndex=' + str(pageIndex) + '&_async_id=offerlist%3Aoffers'
            content = urllib2.urlopen(list_url).read()
            content = self._remove_escape(content)
            if content.find('offerId') == -1:
                break
            offerId_reg = re.compile(r'offerId=(.+?)"')
            data = offerId_reg.findall(content)
            if len(data) == 0:
                break
            for offerId in data:
                site_name = sel.response.url[sel.response.url.find('://') + len('://'):sel.response.url.find('.1688.com')]
                item_url = 'https://detail.1688.com/offer/%s.html?sitename=%s&sku=%s' % (offerId ,site_name ,sku)
                print item_url
                item_urls.append(item_url)
                request = scrapy.Request(item_url, callback=self.parse_item)
                requests.append(request)
                sku += 1
            pageIndex += 1
        return requests

    def find_nexts_from_list_page(self, sel, list_urls):
        """find next pages in category url"""
        #http://m.1688.com/winport/asyncView?memberId=b2b-2847846249efc59&pageIndex=20&_async_id=offerlist%3Aoffers

        return []

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
        features_key_xpath = '//div[@id="mod-detail-attributes"]//table/tbody/tr/td[@class="de-feature"]/text()'
        features_value_xpath = '//div[@id="mod-detail-attributes"]//table/tbody/tr/td[@class="de-value"]/text()'
        key = sel.xpath(features_key_xpath).extract()
        value = sel.xpath(features_value_xpath).extract()
        
        if len(key) != 0 and len(value) != 0:
            item['features'] = dict(zip(key,value))
        item['features']['url'] = sel.response.url[:sel.response.url.find('?sitename=')]
        sitename = sel.response.url[sel.response.url.find('?sitename=') + len('?sitename='):sel.response.url.find('&sku=')]
        sku = sel.response.url[sel.response.url.find('&sku=') + len('&sku='):]
        fd = open(sitename, "a")
        fd.write(sku + ' => ')
        fd.write(json.dumps(item['features'], ensure_ascii=False))
        fd.write("\n")
        fd.close()

    def _extract_description(self, sel, item):
        pass

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        sitename = sel.response.url[sel.response.url.find('?sitename=') + len('?sitename='):sel.response.url.find('&sku=')]
        sku = sel.response.url[sel.response.url.find('&sku=') + len('&sku='):]
        image_url_xpath = '//div[@id="desc-lazyload-container"]/@data-tfs-url'
        data = sel.xpath(image_url_xpath).extract()
        if len(data) != 0:
            content = urllib2.urlopen(data[0]).read()
            content = self._remove_escape(content)
            img_reg = re.compile(r'src="(.+?)"')
            data = img_reg.findall(content)
            imgs = []
            if len(data) != 0:
                for img in data:
                    if img.find('http') == -1:
                        img = 'http:' + img
                    if img.find('jpg') == -1 and img.find('png') == -1:
                        continue
                    imgs.append(img)
                item['image_urls'] = [ img + '?index=' + str(index + 1) + '&sku=' + sku + '&dir=' + sitename for index ,img in enumerate(list(set(imgs)))]

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