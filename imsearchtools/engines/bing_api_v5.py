#!/usr/bin/env python

import requests

try:
    import simplejson as json
except ImportError:
    import json # Python 2.6+ only

from .search_client import *
from .api_credentials import *

## API Configuration
#  --------------------------------------------

BING_API_ENTRY = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search'

DEBUG_MESSAGES = False

## Search Class
#  --------------------------------------------

class BingAPISearchV5(requests.Session, SearchClient):
    """Wrapper class for Bing Image Search API. For more details see:
    http://www.bing.com/developers/
    """

    def __init__(self, async_query=True, timeout=5.0, **kwargs):
        super(BingAPISearchV5, self).__init__()

        if not BING_API_KEY_V5:
            raise NoAPICredentials('API Credentials must be specified in imsearch/engines/api_credentials.py')

        self.headers = { 'Ocp-Apim-Subscription-Key' : BING_API_KEY_V5 }
        self.timeout = timeout

        self._results_per_req = 50
        self._supported_sizes_map = {'small': 'Small',
                                     'medium': 'Medium',
                                     'large': 'Large'}
        self._supported_styles_map = {'photo': 'Photo',
                                      'clipart': 'Clipart',
                                      'lineart': 'Line'}
        self.async_query = async_query

    def _fetch_results_from_offset(self, query, result_offset,
                                   aux_params={}, headers={},
                                   num_results=-1):
        if num_results == -1:
            num_results = self._results_per_req

        try:
            quoted_query = "'%s'" % query

            if DEBUG_MESSAGES:
                print(quoted_query)

            req_result_count = min(self._results_per_req, num_results-result_offset)

            # add query position to auxilary parameters
            aux_params['q'] = quoted_query
            aux_params['offset'] = result_offset
            aux_params['count'] = req_result_count
            if DEBUG_MESSAGES:
                print(aux_params)

            resp = self.get(BING_API_ENTRY, params=aux_params, headers=headers)
            resp.raise_for_status()

            # extract list of results from response
            result_dict = resp.json()
            if DEBUG_MESSAGES:
                print(json.dumps(result_dict))

            return result_dict['value']
        except requests.exceptions.RequestException as e:
            print('error occurred: ' + str(e))
            return []

    def __bing_results_to_results(self, results):
        return [{'url': item['contentUrl'],
                 'image_id': item['imageId'],
                 'title': item['name']} for item in results]

    def query(self, query, size='medium', style='photo', num_results=100):
        # prepare query parameters
        size = self._size_to_native_size(size)
        style = self._style_to_native_style(style)

        aux_params = {}
        if size:
            aux_params['size'] = size
        if style:
            aux_params['imageType'] = style

        # prepare output
        results = []

        # do request
        results = self._fetch_results(query,
                                      num_results,
                                      aux_params=aux_params,
                                      headers=self.headers
                                      )

        return self.__bing_results_to_results(results)

