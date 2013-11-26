import imsearchtools

import requests
import re

class TestGoogleWeb(object):

    def setup(self):
        self._gws = imsearchtools.query.GoogleWebSearch(False)
        self._q = 'polka dots'

    def test_images_returned(self):
        res = self._gws.query(self._q, num_results=100)
        assert len(res) == 100

    def test_ranking_correct(self):
        url = 'https://www.google.com/search'
        aux_params = {}
        aux_params['q'] = self._q
        aux_params['tbm'] = 'isch'
        #aux_params['ijn'] = 0
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:25.0) Gecko/20100101 Firefox/25.0'}

        resp = requests.get(url, params=aux_params, headers=headers)
        resp_str = resp.text

        image_div_pattern = re.compile(r'<div class="rg_di"(.*?)</div>')
        image_url_pattern = re.compile(r'imgurl=(.*?)&')
        #image_id_pattern = re.compile(r'id":"(.*?):')

        image_divs = image_div_pattern.findall(resp_str)
        image_urls = []
        for div in image_divs:
            image_urls.append(image_url_pattern.search(div).group(1))

        res = self._gws.query(self._q,
                              size='', style='',
                              num_results=len(image_urls))
        assert len(res) == len(image_urls)

        for i in range(len(image_urls)):
            assert '%d:%s' % (i, res[i]['url']) == '%d:%s' % (i, image_urls[i])

    
