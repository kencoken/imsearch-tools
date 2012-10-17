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

FLICKR_API_ENTRY = 'http://api.flickr.com/services/rest/'
FLICKR_API_METHOD = 'flickr.photos.search'

## Search Class
#  --------------------------------------------

class FlickrAPISearch(restkit.Resource, SearchClient):
    """Wrapper class for Flickr API. For more details see:
    http://www.flickr.com/services/api/
    """
    
    def __init__(self, **kwargs):
        super(FlickrAPISearch, self).__init__(FLICKR_API_ENTRY, **kwargs)

        self._results_per_req = 100
        self._supported_sizes_map = {'small': 't',
                                     'medium': 'n',
                                     'large': 'c'}
        self._supported_styles_map = {'photo': 'photo'}

    def __fetch_results_from_offset(self, query, result_offset,
                                    num_results=-1,
                                    aux_params={}, headers={}):
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
            aux_params['per_page'] = self._results_per_req
            aux_params['page'] = page_num
            
            resp = self.get(params_dict=aux_params,
                            headers=headers,
                            text=query)

            # extract list of results from response
            result_dict = json.loads(resp.body_string())

            return result_dict['photos']['photo']

        except restkit.errors.RequestError:
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
                 'image_id': item['id'],
                 'title': item['title']} for item in results]

    def __size_to_flickr_size(self, size):
        return self._size_to_native_size(size, self._supported_sizes_map)

    def __style_to_flickr_style(self, style):
        return self._style_to_native_style(style, self._supported_styles_map)

    @property
    def supported_sizes(self):
        return self._supported_sizes_map.keys()

    @property
    def supported_styles(self):
        return self._supported_styles_map.keys()

    def query(self, query, size='medium', num_results=100):
        # prepare query parameters
        size = self.__size_to_flickr_size(size)
        
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
                                      self._results_per_req,
                                      self.__fetch_results_from_offset,
                                      aux_params=aux_params,
                                      async_query=self.async_query)
        
        return self.__flickr_results_to_results(results, size)
    
