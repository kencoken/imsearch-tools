#!/usr/bin/env python

import restkit

try:
    import simplejson as json
except ImportError:
    import json # Python 2.6+ only

from search_client import *
from api_credentials import *

## API Configuration
#  --------------------------------------------

GOOGLE_API_ENTRY = 'https://www.googleapis.com/customsearch/'
GOOGLE_API_FUNC = 'v1'

## Search Class
#  --------------------------------------------

class GoogleAPISearch(restkit.Resource, SearchClient):
    """Wrapper class for Google Custom Search API (for images). For more details see:
    https://developers.google.com/custom-search/v1/overview/
    
    ** NOTE: This updated API only offers search over 'custom search engines' for which
       URLs of specific websites must be specified, although there is an option in the
       control panel to search 'the entire web, preferring listed websites' - apparently
       there is no way to search the web without specifying a list of custom URLs **
    """
    
    def __init__(self, **kwargs):
        super(GoogleAPISearch, self).__init__(GOOGLE_API_ENTRY, **kwargs)

        self._results_per_req = 10
        self._supported_sizes_map = {'small': 'small',
                                     'medium': 'medium',
                                     'large': 'large'}
        self._supported_styles_map = {'photo': 'photo',
                                      'graphics': 'clipart',
                                      'clipart': 'clipart',
                                      'lineart': 'lineart',
                                      'face': 'face',
                                      'news': 'news'}

    def __fetch_results_from_offset(self, query, result_offset,
                                    num_results=-1,
                                    aux_params={}, headers={}):
        if num_results == -1:
            num_results = self._results_per_req
        try:
            req_result_count = min(self._results_per_req, num_results-result_offset)

            # add query position to auxilary parameters
            aux_params['start'] = result_offset + 1
            aux_params['num'] = req_result_count
            
            resp = self.get(GOOGLE_API_FUNC, params_dict=aux_params,
                            headers=headers,
                            q=query)

            # extract list of results from response
            result_dict = json.loads(resp.body_string())

            return result_dict['items']

        except restkit.errors.RequestError:
            return []
        
    def __google_results_to_results(self, results):
        return [{'url': item['pagemap']['cse_image'][0]['src'],
                 'image_id': item['cacheId'],
                 'title': item['title']} for item in results
                if (item.has_key('pagemap')
                    and item['pagemap'].has_key('cse_iamge')
                    and item.has_key('cacheId'))]

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
        # check input
        if num_results > 100:
            raise ValueError('Google API currently allows for a maximum of 100 results to be returend')
        
        # prepare query parameters
        size = self.__size_to_google_size(size)
        style = self.__style_to_google_style(style)

        # prepare auxilary parameter list
        aux_params = {'cx': GOOGLE_API_CX,
                      'key': GOOGLE_API_KEY}
        if size:
            aux_params['imgSize'] = size
        if style:
            aux_params['imgType'] = style

        # do request
        results = self._fetch_results(query,
                                      num_results,
                                      self._results_per_req,
                                      self.__fetch_results_from_offset,
                                      aux_params=aux_params,
                                      async_query=self.async_query)

        return self.__google_results_to_results(results)
