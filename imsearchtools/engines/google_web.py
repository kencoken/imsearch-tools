#!/usr/bin/env python

import restkit
import re

try:
    import simplejson as json
except ImportError:
    import json # Python 2.6+ only

from search_client import *
from api_credentials import *

## API Configuration
#  --------------------------------------------

GOOGLE_WEB_ENTRY = 'http://www.google.com/'
GOOGLE_WEB_FUNC = 'images'

## Search Class
#  --------------------------------------------

class GoogleWebSearch(restkit.Resource, SearchClient):
    """Wrapper class for Google Image Search using web interface.

    This class does not use any API, but instead extracts results directly from the
    web search pages.

    Created November 2010, Updated May 2011, confirmed working October 2012.
    """
    
    def __init__(self, async_query=True, timeout=10.0, **kwargs):
        super(GoogleWebSearch, self).__init__(GOOGLE_WEB_ENTRY, **kwargs)

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
        self.timeout = timeout

    def __fetch_results_from_offset(self, query, result_offset,
                                    num_results=-1,
                                    aux_params={}, headers={}):
        if num_results == -1:
            num_results = self._results_per_req
        image_url_pattern = re.compile(r'/imgres\?imgurl=(.*?)&')
        image_id_pattern = re.compile(r'tbn:(.*?)"')
            
        try:
            # add query position to auxilary parameters
            aux_params['start'] = result_offset

            resp = self.get('images', params_dict=aux_params,
                            headers=headers,
                            q=query)

            resp_str = resp.body_string()
            image_urls = image_url_pattern.findall(resp_str)
            image_ids = image_id_pattern.findall(resp_str)

            resp_dict = [{'url': item[0],
                          'image_id': item[1]} for item in zip(image_urls, image_ids)]

            return resp_dict
        except restkit.errors.RequestError:
            return []

    def __size_to_google_size(self, size):
        return self._size_to_native_size(size, self._supported_sizes_map)

    def __style_to_google_style(self, style):
        return self._style_to_native_style(style, self._supported_styles_map)

    @property
    def supported_sizes(self):
        return self._supported_sizes_map.keys()

    @property
    def supported_styles(self):
        return self._supported_styles_map.keys()
        
    def query(self, query, size='medium', style='photo', num_results=100):
        # prepare query parameters
        size = self.__size_to_google_size(size)
        style = self.__style_to_google_style(style)

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
                                      self._results_per_req,
                                      self.__fetch_results_from_offset,
                                      aux_params=aux_params,
                                      headers=headers,
                                      async_query=self.async_query)

        return results
    
