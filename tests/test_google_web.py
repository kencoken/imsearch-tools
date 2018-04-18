import os
import sys
import requests
import re

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(FILE_DIR, '..'))
from imsearchtools import query as image_query


class TestGoogleWeb(object):

    def setup(self):
        self._gws = image_query.GoogleWebSearch(False)
        self._q = 'polka dots'

    def test_images_returned(self):
        res = self._gws.query(self._q, num_results=100)
        assert len(res) == 100

    def test_ranking_correct(self):
        url = 'https://www.google.com/search'
        aux_params = {}
        aux_params['as_q'] = self._q
        aux_params['tbm'] = 'isch'
        aux_params['imgsz'] = 'm'
        aux_params['imgtype'] = 'photo'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}

        resp = requests.get(url, params=aux_params, headers=headers)
        resp_str = resp.text

        image_div_pattern = re.compile(r'class="rg_meta(.*?)</div>')
        image_url_pattern = re.compile(r'"ou":"(.*?)"')

        image_divs = image_div_pattern.findall(resp_str)
        image_urls = []
        for div in image_divs:
            image_urls.append(image_url_pattern.search(div).group(1))

        # test1: the GET and the QUERY return the same number of results
        res = self._gws.query(self._q, size='medium', style='photo',
                              num_results=len(image_urls))
        assert len(res) == len(image_urls)

        # test2: two consecutive QUERYS return the same number of results
        res2 = self._gws.query(self._q, size='medium', style='photo',
                               num_results=len(image_urls))
        assert len(res) == len(res2)

        # test3: two consecutive QUERYS contain the same urls as result (not necessarily in the same order)
        for item_res in res:
            found = False
            for item_res2 in res2:
                if item_res['url'] == item_res2['url']:
                    found = True
                    break
            assert found


test = TestGoogleWeb()
test.setup()
test.test_images_returned()
test.test_ranking_correct()
