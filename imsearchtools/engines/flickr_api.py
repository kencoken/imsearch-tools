#!/usr/bin/env python

import requests
from hashlib import md5

from search_client import *
from api_credentials import *

## API Configuration
#  --------------------------------------------

FLICKR_API_ENTRY = 'http://api.flickr.com/services/rest/'
FLICKR_API_METHOD = 'flickr.photos.search'

## Search Class
#  --------------------------------------------

class FlickrAPISearch(requests.Session, SearchClient):
    """Wrapper class for Flickr API. For more details see:
    http://www.flickr.com/services/api/
    """

    def __init__(self, async_query=True, timeout=5.0, **kwargs):
        super(FlickrAPISearch, self).__init__()

        if not FLICKR_API_KEY or not FLICKR_API_SECRET:
            raise NoAPICredentials('API Credentials must be specified in imsearch/engines/api_credentials.py')

        self.headers.update(kwargs)
        self.timeout = timeout

        self._results_per_req = 100
        self._supported_sizes_map = {'small': 't',
                                     'medium': 'n',
                                     'large': 'c'}
        self._supported_styles_map = {'photo': 'photo'}

        self.async_query = async_query

    def _fetch_results_from_offset(self, query, result_offset,
                                   aux_params={}, headers={},
                                   num_results=-1):
        if num_results == -1:
            num_results = self._results_per_req
        try:
            # convert offset to page number
            if num_results > self._results_per_req:
                raise ValueError("num_results should be (%d) <= self._results_per_req (%d)" %
                                 num_results, self._results_per_req)
            if result_offset % float(self._results_per_req):
                raise ValueError("Offset for Flickr API must be a multiple of self._results_per_req (%d)" %
                                 self._results_per_req)
            page_num = result_offset / self._results_per_req
            # add query position to auxilary parameters
            aux_params['text'] = query
            aux_params['per_page'] = self._results_per_req
            aux_params['page'] = page_num

            resp = self.get(FLICKR_API_ENTRY,
                            params=aux_params,
                            headers=headers)
            resp.raise_for_status()

            # extract list of results from response
            result_dict = resp.json()

            return result_dict['photos']['photo'][:(num_results-result_offset)]

        except requests.exceptions.RequestException:
            return []

    def __flickr_results_to_results(self, results, size=None):
        if size:
            size = '_%s' % size
        flickr_api_img_url = 'http://farm%s.staticflickr.com/%s/%s_%s%s.jpg'
        return [{'url': flickr_api_img_url % (item['farm'],
                                              item['server'],
                                              item['id'],
                                              item['secret'],
                                              size),
                 'image_id': md5(item['id']).hexdigest(),
                 'title': item['title']} for item in results]

    def query(self, query, size='medium', num_results=100):
        # prepare query parameters
        size = self._size_to_native_size(size)

        # prepare auxilary parameter list
        aux_params = {'method': FLICKR_API_METHOD,
                      'api_key': FLICKR_API_KEY,
                      'format': 'json',
                      'nojsoncallback': 1,
                      'sort': 'relevance',
                      'content_type': 1} # just photos

        # do request
        results = self._fetch_results(query,
                                      num_results,
                                      aux_params=aux_params)

        return self.__flickr_results_to_results(results, size)
