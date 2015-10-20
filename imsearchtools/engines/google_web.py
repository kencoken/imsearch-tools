#!/usr/bin/env python

import requests
import re
import math
from hashlib import md5

from search_client import *
from api_credentials import *

## API Configuration
#  --------------------------------------------

GOOGLE_WEB_ENTRY = 'http://www.google.com/'
GOOGLE_WEB_FUNC = 'search'

## Search Class
#  --------------------------------------------

class GoogleWebSearch(requests.Session, SearchClient):
    """Wrapper class for Google Image Search using web interface.

    This class does not use any API, but instead extracts results directly from the
    web search pages (acting as Firefox v25.0).

    Created November 2013.
    """

    def __init__(self, async_query=True, timeout=5.0, **kwargs):
        super(GoogleWebSearch, self).__init__()

        self.headers.update(kwargs)
        self.timeout = timeout

        self._results_per_req = 100
        self._supported_sizes_map = {'small': 's',
                                     'medium': 'm',
                                     'large': 'l'}
        self._supported_styles_map = {'photo': 'photo',
                                      'graphics': 'clipart',
                                      'clipart': 'clipart',
                                      'lineart': 'lineart',
                                      'face': 'face'}
        self.async_query = async_query

    def _fetch_results_from_offset(self, query, result_offset,
                                   aux_params={}, headers={},
                                   num_results=-1):
        #if num_results == -1:
        #    num_results = self._results_per_req
        image_div_pattern = re.compile(r'<div class="rg_di(.*?)</div>')
        image_url_pattern = re.compile(r'imgurl=(.*?)&')
        #image_id_pattern = re.compile(r'id":"(.*?):')
        image_id_pattern = re.compile(r'name="(.*?):')

        try:
            page_idx = int(math.floor(result_offset/float(self._results_per_req)))
            page_start = page_idx*self._results_per_req
            page_offset = result_offset - page_start

            # add query position to auxilary parameters
            aux_params['q'] = query
            aux_params['ijn'] = page_idx  # ijn is the AJAX page index (0 = first page)
            #aux_params['start'] = page_idx*self._results_per_req # apparently not necessary

            resp = self.get(GOOGLE_WEB_ENTRY + GOOGLE_WEB_FUNC,
                            params=aux_params, headers=headers)
            resp_str = resp.text

            image_divs = image_div_pattern.findall(resp_str)
            image_data = []
            for div in image_divs:
                image_url_match = image_url_pattern.search(div)
                image_id_match = image_id_pattern.search(div)
                if image_url_match and image_id_match:
                    image_data.append((image_url_match.group(1),
                                       image_id_match.group(1)))

            # modify returned results list according to input params
            # (if necessary)
            if page_offset >= len(image_data):
                image_data = []
            else:
                image_data = image_data[page_offset:]
            if num_results > 0 and len(image_data) > num_results:
                image_data = image_data[:num_results]

            # package for output
            resp_dict = [{'url': item[0],
                          'image_id': md5(item[1]).hexdigest(),
                          'rank': result_offset+index+1} for index, item in enumerate(image_data)]

            return resp_dict
        except requests.exceptions.RequestException:
            return []

    def query(self, query, size='medium', style='photo', num_results=100):
        # prepare query parameters
        size = self._size_to_native_size(size)
        style = self._style_to_native_style(style)

        # prepare auxilary parameters (contained in tbs)
        tbs_list = []
        if size:
            tbs_list.append('isz:%s' % size)
        if style:
            tbs_list.append('itp:%s' % style)

        tbs_str = ','.join(tbs_list)

        # prepare shared parameters
        aux_params = {}
        aux_params['tbm'] = 'isch' #image search mode
        aux_params['ijn'] = 0      # causes AJAX request contents only to be returned
        if tbs_str:
            aux_params['tbs'] = tbs_str

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:25.0) Gecko/20100101 Firefox/25.0'}

        # do request
        results = self._fetch_results(query,
                                      num_results,
                                      aux_params=aux_params,
                                      headers=headers)

        return results
