#!/usr/bin/env python

import restkit
from hashlib import md5

try:
    import simplejson as json
except ImportError:
    import json # Python 2.6+ only

from search_client import *
from api_credentials import *

## API Configuration
#  --------------------------------------------

GOOGLE_OLD_API_ENTRY = 'https://ajax.googleapis.com/ajax/services/search/'
GOOGLE_OLD_API_FUNC = 'images'

## Search Class
#  --------------------------------------------

class GoogleOldAPISearch(restkit.Resource, SearchClient):
    """Wrapper class for Google Image Search API. For more details see:
    https://developers.google.com/image-search/
    
    ** NOTE: As of 26 May 2011 the Image Search API has been deprecated **
    """
    
    def __init__(self, async_query=True, timeout=5.0, **kwargs):
        super(GoogleOldAPISearch, self).__init__(GOOGLE_OLD_API_ENTRY, **kwargs)

        self._results_per_req = 8
        self._supported_sizes_map = {'small': 'small',
                                     'medium': 'medium|large|xlarge',
                                     'large': 'xxlarge|huge'}
        self._supported_styles_map = {'photo': 'photo',
                                      'graphics': 'clipart|lineart',
                                      'clipart': 'clipart',
                                      'lineart': 'lineart',
                                      'face': 'face'}
        self.async_query = async_query
        self.timeout = timeout

    def _fetch_results_from_offset(self, query, result_offset,
                                   aux_params={}, headers={},
                                   num_results=-1):
        if num_results == -1:
            num_results = self._results_per_req
        try:
            req_result_count = min(self._results_per_req, num_results-result_offset)

            # add query position to auxilary parameters
            aux_params['start'] = result_offset
            aux_params['rsz'] = req_result_count
            
            resp = self.get(GOOGLE_OLD_API_FUNC, params_dict=aux_params,
                            headers=headers,
                            q=query)

            # extract list of results from response
            result_dict = json.loads(resp.body_string())

            return result_dict['responseData']['results']

        except restkit.errors.RequestError:
            return []

    def __google_results_to_results(self, results):
        return [{'url': item['unescapedUrl'],
                 'image_id': md5(item['imageId']).hexdigest(),
                 'title': item['titleNoFormatting']} for item in results]

    def __size_to_google_size(self, size):
        return self._size_to_native_size(size)

    def __style_to_google_style(self, style):
        return self._style_to_native_style(style)

    @property
    def supported_sizes(self):
        return self._supported_sizes_map.keys()

    @property
    def supported_styles(self):
        return self._supported_styles_map.keys()

    def query(self, query, size='medium', style='photo', num_results=64):
        # check input
        if num_results > 64:
            raise ValueError('Google API currently allows for a maximum of 64 results to be returend')
        
        # prepare query parameters
        size = self.__size_to_google_size(size)
        style = self.__style_to_google_style(style)

        # prepare auxilary parameter list
        aux_params = {'v': '1.0',
                      'key': GOOGLE_OLD_API_KEY}
        if size:
            aux_params['imgsz'] = size
        if style:
            aux_params['imgtype'] = style

        # prepare output
        results = []

        # do request
        results = self._fetch_results(query,
                                      num_results,
                                      aux_params=aux_params)

        return self.__google_results_to_results(results)
    
