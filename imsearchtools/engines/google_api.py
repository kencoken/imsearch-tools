#!/usr/bin/env python

import requests
from hashlib import md5

from search_client import *
from api_credentials import *

## API Configuration
#  --------------------------------------------

GOOGLE_API_ENTRY = 'https://www.googleapis.com/customsearch/'
GOOGLE_API_FUNC = 'v1'

## Search Class
#  --------------------------------------------

class GoogleAPISearch(requests.Session, SearchClient):
    """Wrapper class for Google Custom Search API (for images). For more details see:
    https://developers.google.com/custom-search/v1/overview/

    ** NOTE: This updated API only offers search over 'custom search engines' for which
       URLs of specific websites must be specified, although there is an option in the
       control panel to search 'the entire web, preferring listed websites' - apparently
       there is no way to search the web without specifying a list of custom URLs **
    """

    def __init__(self, async_query=True, timeout=5.0, **kwargs):
        super(GoogleAPISearch, self).__init__()

        if not GOOGLE_API_KEY or not GOOGLE_API_CX:
            raise NoAPICredentials('API Credentials must be specified in imsearch/engines/api_credentials.py')

        self.headers.update(kwargs)
        self.timeout = timeout

        self._results_per_req = 10
        self._supported_sizes_map = {'small': 'medium',
                                     'medium': 'large',
                                     'large': 'xxlarge'}
        self._supported_styles_map = {'photo': 'photo',
                                      'graphics': 'clipart',
                                      'clipart': 'clipart',
                                      'lineart': 'lineart',
                                      'face': 'face',
                                      'news': 'news'}
        self.async_query = async_query

    def _fetch_results_from_offset(self, query, result_offset,
                                   aux_params={}, headers={},
                                   num_results=-1):
        if num_results == -1:
            num_results = self._results_per_req
        try:
            req_result_count = min(self._results_per_req, num_results-result_offset)

            # add query position to auxilary parameters
            aux_params['q'] = query
            aux_params['start'] = result_offset + 1
            aux_params['num'] = req_result_count

            resp = self.get(GOOGLE_API_ENTRY + GOOGLE_API_FUNC,
                            params=aux_params, headers=headers)
            resp.raise_for_status()

            # extract list of results from response
            result_dict = resp.json()

            return result_dict['items'][:(num_results-result_offset)]

        except requests.exceptions.RequestException:
            return []

    def __google_results_to_results(self, results):
        return [{'url': item['link'],
                 'image_id': md5(item['link']).hexdigest(),
                 'title': item['title']} for item in results]

    def query(self, query, size='medium', style='photo', num_results=100):
        # check input
        if num_results > 100:
            raise ValueError('Google API currently allows for a maximum of 100 results to be returend')

        # prepare query parameters
        size = self._size_to_native_size(size)
        style = self._style_to_native_style(style)

        # prepare auxilary parameter list
        aux_params = {'cx': GOOGLE_API_CX,
                      'key': GOOGLE_API_KEY,
                      'searchType': 'image'}
        if size:
            aux_params['imgSize'] = size
        if style:
            aux_params['imgType'] = style

        # do request
        results = self._fetch_results(query,
                                      num_results,
                                      aux_params=aux_params)

        return self.__google_results_to_results(results)
