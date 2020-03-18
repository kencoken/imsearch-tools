import os
import sys
import requests
import re

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(FILE_DIR, '..'))
from imsearchtools.engines import google_web as image_query

class TestGoogleWeb(object):

    def setup(self):
        self._gws = image_query.GoogleWebSearch(False)
        self._q = 'polka dots'

    def _url_clean_up(self, url):
        """
        Some extracted urls can include search parameters after the image file name or can contain complicated encoded redirections.
        This method does its best to clean up image url. After that it just assumes the url is correct and returns it.
        """
        if url != None and url != "":
            if '?' in url:
                url = url.split('?')[0]
            if '\\' in url:
                url = url.split('\\')[0]
            if '$' in url:
                url = url.split('$')[0]
            # add further filter her is necessary
        return url

    def test_images_returned(self):
        print ("**test_images_returned")
        res = self._gws.query(self._q, num_results=100)
        print (len(res))
        # do not compare with num_results=100 below because
        # urls can be filtered out during the query, after
        # getting them from google. Just test that we are getting
        # **some** urls
        assert len(res) > 0

    def test_ranking_correct(self):
        print ("**test_ranking_correct")
        url = 'http://www.google.com/search'
        aux_params = {}
        aux_params['as_q'] = self._q
        aux_params['tbm'] = 'isch'
        aux_params['imgsz'] = 'm'
        aux_params['ijn'] = 0
        aux_params['imgtype'] = 'photo'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}

        resp = requests.get(url, params=aux_params, headers=headers)
        resp_str = resp.text

        image_div_pattern = re.compile(r'class="rg_meta(.*?)</div>')
        image_url_pattern = re.compile(r'"ou":"(.*?)"')

        image_divs = image_div_pattern.findall(resp_str)

        image_urls = []
        for div in image_divs:
            image_url_match = image_url_pattern.search(div)
            url = image_url_match.group(1)
            url = self._url_clean_up(url)
            name = url.rsplit('/', 1)[-1]
            if url and name:
                image_urls.append(url)

        print ("URLs after standard GET:", len(image_urls))
        # test1: the GET and the QUERY return the same number of results
        print ("test1: the GET and the QUERY return the same number of results")
        res = self._gws.query(self._q, size='medium', style='photo',
                              num_results=len(image_urls))
        print ("URLs after QUERY", len(res))
        assert len(res) == len(image_urls)

        # test2: two consecutive QUERYS return the same number of results
        print ("test2: two consecutive QUERYS return the same number of results")
        res2 = self._gws.query(self._q, size='medium', style='photo',
                               num_results=len(image_urls))
        print ("URLs after second QUERY", len(res2))
        assert len(res) == len(res2)

        # test3: two consecutive QUERYS contain the same urls as result (not necessarily in the same order)
        print ("test3: two consecutive QUERYS contain the same urls as result (not necessarily in the same order)")
        for item_res in res:
            found = False
            for item_res2 in res2:
                if item_res['url'] == item_res2['url']:
                    found = True
                    break
            assert found
        print ("URLs are the same")


test = TestGoogleWeb()
test.setup()
test.test_images_returned()
test.test_ranking_correct()
