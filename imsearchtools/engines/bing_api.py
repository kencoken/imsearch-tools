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

BING_API_ENTRY = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/'
BING_API_FUNC = 'Image'

## Search Class
#  --------------------------------------------

class BingAPISearch(restkit.Resource, SearchClient):
    """Wrapper class for Bing Image Search API. For more details see:
    http://www.bing.com/developers/
    """

    def __init__(self, async_query=True, timeout=5.0, **kwargs):
        auth = restkit.BasicAuth('', BING_API_KEY)
        super(BingAPISearch, self).__init__(BING_API_ENTRY, filters=[auth], **kwargs)

        self._results_per_req = 50
        self._supported_sizes_map = {'small': 'Small',
                                     'medium': 'Medium',
                                     'large': 'Large'}
        self._supported_styles_map = {'photo': 'Photo',
                                      'graphics': 'Graphics'}
        self.async_query = async_query
        self.timeout = timeout

    def _fetch_results_from_offset(self, query, result_offset,
                                   aux_params={}, headers={},
                                   num_results=-1):
        if num_results == -1:
            num_results = self._results_per_req
            
        try:
            quoted_query = "'%s'" % query

            req_result_count = min(self._results_per_req, num_results-result_offset)

            # add query position to auxilary parameters
            aux_params['$skip'] = result_offset
            aux_params['$top'] = req_result_count

            resp = self.get(BING_API_FUNC, params_dict=aux_params,
                            headers=headers,
                            Query=quoted_query)

            # extract list of results from response
            result_dict = json.loads(resp.body_string())

            return result_dict['d']['results']
        except restkit.errors.RequestError:
            return []

    def __bing_results_to_results(self, results):
        return [{'url': item['MediaUrl'],
                 'image_id': md5(item['ID']).hexdigest(),
                 'title': item['Title']} for item in results]
    
    def query(self, query, size='medium', style='photo', num_results=100):
        # prepare query parameters
        size = self._size_to_native_size(size)
        style = self._style_to_native_style(style)
        
        image_filters_list = []
        if size:
            image_filters_list.append('Size:%s' % size)
        if style:
            image_filters_list.append('Style:%s' % style)
        image_filters = '+'.join(image_filters_list)
        quoted_image_filters = None # of form: 'Size=<size>+Style=<style>'
        if image_filters:
            quoted_image_filters = "'%s'" % image_filters

        # prepare auxilary parameters
        aux_params = {'$format': 'JSON'}
        if quoted_image_filters:
            aux_params['ImageFilters'] = quoted_image_filters

        # prepare output
        results = []

        # do request
        results = self._fetch_results(query,
                                      num_results,
                                      aux_params=aux_params)

        return self.__bing_results_to_results(results)
    
