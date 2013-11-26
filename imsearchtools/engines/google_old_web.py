#!/usr/bin/env python

import requests
import re
from hashlib import md5

from search_client import *
from api_credentials import *

## API Configuration
#  --------------------------------------------

GOOGLE_WEB_ENTRY = 'http://www.google.com/'
GOOGLE_WEB_FUNC = 'images'

## Search Class
#  --------------------------------------------

class GoogleOldWebSearch(requests.Session, SearchClient):
    """Wrapper class for Google Image Search using web interface.

    This class does not use any API, but instead extracts results directly from the
    web search pages (acting as Internet Explorer 7.0).

    Created November 2010, Updated May 2011, confirmed working October 2012.

    Broken as of November 2013.
    """
    
    def __init__(self, async_query=True, timeout=5.0, **kwargs):
        super(GoogleOldWebSearch, self).__init__()

        self.headers.update(kwargs)
        self.timeout = timeout

        self._results_per_req = 20
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
        if num_results == -1:
            num_results = self._results_per_req
        image_url_pattern = re.compile(r'/imgres\?imgurl=(.*?)&')
        image_id_pattern = re.compile(r'tbn:(.*?)"')
            
        try:
            # add query position to auxilary parameters
            aux_params['q'] = query
            aux_params['start'] = result_offset

            resp = self.get(GOOGLE_WEB_ENTRY + GOOGLE_WEB_FUNC,
                            params=aux_params, headers=headers)

            resp_str = resp.text
            image_urls = image_url_pattern.findall(resp_str)[:(num_results-result_offset)]
            image_ids = image_id_pattern.findall(resp_str)[:(num_results-result_offset)]

            resp_dict = [{'url': item[0],
                          'image_id': md5(item[1]).hexdigest()} for item in zip(image_urls, image_ids)]

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
        
        aux_params = {}
        if tbs_str:
            aux_params['tbs'] = tbs_str
            
        headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)'}

        # do request
        results = self._fetch_results(query,
                                      num_results,
                                      aux_params=aux_params,
                                      headers=headers)
        
        return results
    
