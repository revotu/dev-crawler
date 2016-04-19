# -*- coding: utf-8 -*-
# @author: zhangliangliang

import scrapy.cmdline

import re

import json

import urllib2, cookielib

from avarsha_spider import AvarshaSpider


_spider_name = 'gap'

class GapSpider(AvarshaSpider):
    name = _spider_name
    allowed_domains = ["gap.com"]

    def __init__(self, *args, **kwargs):
        self.header = {'Cookie' : \
            ('ABSegOverride=off; dtm_token=AQEDdX0nLWnwEAEKkhq9AQEIPwE; '
            'SurveyPersist=surveyType%3DRockbridgeSurvey; '
            'ASP1V=3jbATImrW3xcETA8Kw7ioh1LHkTKzimZ-sjnwHpICz22pm8HiNJM_Vg; '
            'omniSessionProducts=strProductsInBag%3D; '
            'mktGlobalSession=gb_disruptor%3D1; '
            'JSESSIONID=5c529903-707f-4e13-b185-b57a32a02060; '
            's_sess=%20s_cc%3Dtrue%3B%20s_sq%3D%3B; '
            's_vi=[CS]v1|2A9D8819850135EA-6000014780001472[CE]; '
            'globalSession=pm-pageLoadTimeDeltaFromPreviousPage%3D%26pm-'
            'domReadyTimeDeltaFromPreviousPage%3D%26pm-undefined%3D%26pm-'
            'outfitPageReadyTimeDeltaFromPreviousPage%3D%26pm-outfitDataReq'
            'uestTimeDeltaFromPreviousPage%3D%26pm-outfitDataLoadTimeDeltaFrom'
            'PreviousPage%3D%26pm-outfitDataLoadTimeDeltaPerProductFromPrevious'
            'Page%3D%26pm-outfitAddToBagDoneTimeDeltaFromPreviousPage%3D%26pm-'
            'outfitAddToBagDoneTimeDeltaPerProductFromPreviousPage%3D%26previ'
            'ousPageUrl%3D/browse/category.do%253Fcid%253D8792%2526department'
            'Redirect%253Dtrue%26previousPageUnloadDate%3D1433556672674%26pre'
            'viousPageName%3Dgp%253Abrowse.siteSearch.en_US%26previousPageBus'
            'inessId%3D5058%26pm-timeToReadyFromPreviousPage%3D3925%26timeToL'
            'oadFromPreviousPage%3Dnull%26xlinkFrom%3D%26pm-categoryId%3Dunde'
            'fined%26pm-quicklookDelta%3Dnull%26pm-addToBagDelta%3Dnull%26pm-f'
            'irstFacetedDataDelta%3D1044; checkoutMode=isEnhanced%3Dtrue; '
            'mktUniversalPersist=respNavSeg4%3DsegB%26NAV2FACETS_1306A_v2_'
            'GROUP_TEST%3DnavGroupSEGB%26responsiveShoppingBagMode%3Drespon'
            'siveBag_SegB%26041415GapEBBSegABTest%3D041415GapEBBSegB%26wish'
            'list2%3DsegB%26OutfitPrototypeABTest3%3DOutfitPrototypeSegB%26'
            'testGFOL0423%3DtestGFOL0423_SegC%26ProdRecPlace041415%3DPRPlaceS'
            'egD%26GOL_hasSeenEmailpop%3D1%26042415GapPopUpABTest%3D042415Gap'
            'PopupSegB%26GAC_AB05052015_000%3Dundefined%26testGFOL0522%3Dtest'
            'GFOL0522_SegC%260531dashboardABTest%3D0531dashboardSegA%26casting'
            'CallPlacement%3DcastCallSeg%26GAC_AB05052015_002%3DGAC_AB0505201'
            '5_002_SegC%26ATOLProdFeedABTest_S2%3DATOLProdFeedSegC%26enableBi'
            'llingModuleEnhancements%3DenableBillingModuleEnhancements_SegB%2'
            '6enablePromoExpandCollapse%3DenablePromoExpandCollapse_SegB; '
            's_pers=%20s_fid%3D6C3BEDDC9A4B48E6-2CA84E7AA9FE6D6D%7C149671422'
            '6203%3B%20s_dfa%3Dgapproduction%252Cgapgidproduction%7C143355847'
            '4768%3B; gcoMode=seg%3DA; gcahMode=seg%3DA; gid.h=016|||; '
            'ABSeg=BSeg; locale=en_US|||; unknownShopperId=0531C84FADCE993578'
            '9FDAF14B8B2C29|||; omniSession=strProductCountInBag%3D0%26firstV'
            'isit%3Dtrue%26strSearchedKeyword%3D%26strPersistSearchedKeyword%'
            '3Dswim%26strSearchedDivision%3D%26strPageNameOfKeywordSearch%3D%'
            '26strPathOfKeywordSearch%3D%26strNumberOfSearchResults%3D277%26'
            'isSiteSearchActive%3Dtrue%26strFSHierarchy1%3Dnon-SBS%2520and%25'
            '20non-FS%26strFSRefinement1%3Dno%2520refinements%26strIsSortBySe'
            'lected%3Dfalse; pixelManagementPersist=pixelPartnerList%3Ddouble'
            'Click_2011/10/20-2020/10/24%252CrangeDoubleClick_2011/10/20-2020'
            '/10/24%252CgoogleAdServices_2011/01/26-2020/01/26%252CbrightTa'
            'g_2011/07/19-2020/07/19')}
        super(GapSpider, self).__init__(*args, **kwargs)

    def convert_url(self, url):
        return url.replace('#', '&')

    def find_items_from_list_page(self, sel, item_urls):
        """parse items in category page"""
        idx = sel.response.url.find('search.do?searchText=')
        if idx != -1:
            idx1 = sel.response.url.find('&', idx)
            if idx1 == -1:
                searchText = sel.response.url[idx + \
                    len('search.do?searchText='):].replace('+', '!2B')
            else:
                searchText = sel.response.url[idx + \
                    len('search.do?searchText='):idx1].replace('+', '!2B')
            match = re.search(re.compile('department=\d+'), sel.response.url)
            if match == None:
                department = ''
            else:
                department = '&' + match.group()

            match = re.search(re.compile('style=[\w\,]+'), sel.response.url)
            if match == None:
                style = ''
            else:
                style = '&' + match.group()
        else:
            match = re.search(re.compile('cid=\d+'), sel.response.url)
            if match == None:
                return
            else:
                cid = match.group()[4:]

            match = re.search(re.compile('style=[\w\,]+'), sel.response.url)
            if match == None:
                style = ''
            else:
                style = match.group()[6:]
        pageid = 0
        requests = []
        while True:
            if idx == -1:
                category_url = ('http://www.gap.com/resources/productSearch/'
                    'v1/search?isFacetsEnabled=true&pageId=%d&cid=%s&'
                    'globalShippingCountryCode=us&locale=en_US&style=%s'
                    '&segment=segB' % (pageid, cid, style))
            else:
                category_url = ('http://www.gap.com/resources/productSearch/v1/'
                    '%s?isFacetsEnabled=true&pageId=%d&'
                    'globalShippingCountryCode=us&locale=en_US'
                    '%s%s&segment=segB' % \
                    (searchText, pageid, department, style))
            request = urllib2.Request(category_url, headers=self.header)
            response = urllib2.urlopen(request)
            data = json.loads(response.read())
            if idx == -1:
                category = (data['productCategoryFacetedSearch']\
                    ['productCategory']['childCategories'])
                if dict == type(category):
                    for childProduct in category['childProducts']:
                        self.find_parse_items(childProduct, item_urls, requests)
                elif list == type(category):
                    for childProducts in category:
                        for childProduct in childProducts['childProducts']:
                            self.find_parse_items(childProduct, \
                                item_urls, requests)
            else:
                category = (
                    data['productCategoryFacetedSearch']['productCategory'])
                for childProduct in category['childProducts']:
                    self.find_parse_items(childProduct, item_urls, requests)

            maxpage = (int(data['productCategoryFacetedSearch']\
                ['productCategory'].get('productCategoryPaginator')\
                .get('pageNumberTotal')) - 1)
            if pageid >= maxpage:
                break
            pageid += 1
        return requests

    def find_parse_items(self, childProduct, item_urls, requests):
        pid = childProduct['businessCatalogItemId']
        item_url = 'http://www.gap.com/browse/product.do?pid=' + pid
        item_urls.append(item_url)
        requests.append(scrapy.Request(item_url, \
            callback=self.parse_item))

    def find_nexts_from_list_page(self, sel, list_urls):
        return []

    def _extract_url(self, sel, item):
        item['url'] = sel.response.url

    def _extract_title(self, sel, item):
        title_xpath = '//div[@id="productNameText"]/h1/text()'
        data = sel.xpath(title_xpath).extract()
        idx1 = 0
        while idx1 < len(data):
            data[idx1] = data[idx1].replace('\n', '').replace('\r', '')\
                .replace('\t', '').strip()
            idx1 += 1
        if len(data) != 0:
            item['title'] = ' '.join(data)

    def _extract_store_name(self, sel, item):
        item['store_name'] = 'Gap'

    def _extract_brand_name(self, sel, item):
        item['brand_name'] = 'Gap'

    def _extract_sku(self, sel, item):
        line = sel.response.url
        if len(line) != 0:
            item['sku'] = line[-9:-3]

    def _extract_features(self, sel, item):
        pass

    def _extract_description(self, sel, item):
        description_xpath = '//div[@id="tabWindow"]/noscript//ul/*'
        data = sel.xpath(description_xpath).extract()
        if len(data) != 0:
            content = ''
            for line in data:
                content += line + ' '
            item['description'] = content

    def _extract_size_chart(self, sel, item):
        pass

    def _extract_color_chart(self, sel, item):
        pass

    def _extract_image_urls(self, sel, item):
        base_url = 'http://www.gap.com/browse/productData.do?pid='
        url = base_url + sel.response.url[-9:-3]
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        f = opener.open(url, '')
        data = f.read()
        imgs = []
        for line in data.split(','):
            if line.find('AV9_Z') != -1:
                continue
            idx1 = line.find('Z\': \'')
            if idx1 != -1:
                idx2 = line.find('jpg\'', idx1)
                img_url = 'http://www.gap.com' + \
                    line[idx1 + len('Z\': \''):idx2] + 'jpg'
                imgs.append(img_url)
        item['image_urls'] = imgs
        f.close()

    def _extract_colors(self, sel, item):
        color_list_xpath = '//div[@id="tabWindow"]/noscript/text()'
        data = sel.xpath(color_list_xpath).extract()
        idx1, idx2 = 0, 0
        while idx1 < len(data):
            if '$' in data[idx1]:
                data[idx2] = data[idx1]
                data[idx2] = data[idx2].replace('\n', '').replace('\r', '')\
                    .replace('\t', '').strip()
                idx3 = data[idx2].find('-')
                if idx3 != -1:
                    data[idx2] = data[idx2][:idx3].strip()
                    idx2 += 1
            idx1 += 1
        data = data[:idx2]
        if len(data) != 0:
            item['colors'] = data

    def _extract_sizes(self, sel, item):
        pass

    def _extract_stocks(self, sel, item):
        pass

    def _extract_price(self, sel, item):
        price_xpath = '//div[@id="tabWindow"]/noscript/text()'
        data = sel.xpath(price_xpath).extract()
        idx1, idx2 = 0, 0
        while idx1 < len(data):
            if '$' in data[idx1]:
                data[idx2] = data[idx1]
                data[idx2] = data[idx2].replace('\n', '').replace('\r', '')\
                    .replace('\t', '').strip()
                idx3 = data[idx2].find('-')
                data[idx2] = data[idx2][idx3 + 1:].strip()
                idx2 += 1
            idx1 += 1
        data = data[:idx2]
        if len(data) != 0:
            price_number = data[0][len('$'):].strip()
            item['price'] = self._format_price('USD ', price_number)

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
        url = sel.response.url
        indx1 = url.find("pid=") + len('pid=')
        indx2 = url.find(",", indx1)
        id = ''
        if indx2 != -1:
            id = url[indx1:indx2]
        else:
            id = url[indx1:]
        review_url0 = ('http://api.bazaarvoice.com/data/batch.json?passkey=tpy1b18t8bg5lp4y9hfs0qm31' +
                       '&apiversion=5.5&displaycode=3755_4_0-en_us&resource.q0=products&filter.q0=id%3Aeq%3Aidnum' +
                       '&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_CA%2Cen_US' +
                       '&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_CA%2Cen_US&resource.q1=reviews' +
                       '&filter.q1=isratingsonly%3Aeq%3Afalse&filter.q1=productid%3Aeq%3Aidnum' +
                       '&filter.q1=contentlocale%3Aeq%3Aen_CA%2Cen_US&sort.q1=submissiontime%3Adesc' +
                       '&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors%2Cproducts%2Ccomments' +
                       '&filter_reviews.q1=contentlocale%3Aeq%3Aen_CA%2Cen_US&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen_CA%2Cen_US' +
                       '&filter_comments.q1=contentlocale%3Aeq%3Aen_CA%2Cen_US&limit.q1=')
        review_url0 = review_url0.replace('idnum', id)

        review_url = review_url0 + str(10) + '&offset.q1=0'
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('{')
        indx2 = content.rfind('}')
        content = content[indx1:indx2 + 1]
        review_dict = json.loads(content)
        review_q1 = review_dict['BatchedResults']['q1']
        review_includes = review_q1['Includes']
        review_count = 0
        if ('Products' in review_includes.keys()):
            if(id in review_includes['Products'].keys()):
                review_count = int(review_includes['Products'][id]['ReviewStatistics']['TotalReviewCount'])
            else:
                item['review_count'] = 0
                return []
        else:
            item['review_count'] = 0
            return []
        item['review_count'] = review_count
        if review_count == 0:
            return []
        item['max_review_rating'] = 5
        item['review_rating'] = float(review_includes['Products'][id]['ReviewStatistics']['AverageOverallRating'])
        review_countRatingsOnly = int(review_includes['Products'][id]['ReviewStatistics']['RatingsOnlyReviewCount'])
        if(review_count <= review_countRatingsOnly):
            return []
        review_url = review_url0 + str(review_count) + '&offset.q1=0'
        content = ''
        request = urllib2.Request(review_url)
        response = urllib2.urlopen(request)
        content = response.read()
        indx1 = content.find('{')
        indx2 = content.rfind('}')
        content = content[indx1:indx2 + 1]
        review_dict = json.loads(content)
        review_q1 = review_dict['BatchedResults']['q1']

        review_results = review_q1['Results']
        review_list = []
        for idx in range(len(review_results)):
            rating = float(review_results[idx]['Rating'])
            date = review_results[idx]['SubmissionTime']
            name = review_results[idx]['UserNickname']
            title = review_results[idx]['Title']
            contents = review_results[idx]['ReviewText']
            review_list.append({'rating':rating,
              'date':date,
              'name':name,
              'title':title,
              'content':contents})
        item['review_list'] = review_list



def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', _spider_name])

if __name__ == '__main__':
    main()
