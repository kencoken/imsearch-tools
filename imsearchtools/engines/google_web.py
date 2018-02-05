#!/usr/bin/env python

import requests
import re
import math
from hashlib import md5

from search_client import *

## Engine Configuration
#  --------------------------------------------

GOOGLE_WEB_ENTRY = 'http://www.google.com/'
GOOGLE_WEB_FUNC = 'search'

## Search Class
#  --------------------------------------------

class GoogleWebSearch(requests.Session, SearchClient):
    """Wrapper class for Google Image Search using web interface.
    See https://www.google.com/advanced_image_search

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
                                      'clipart': 'clipart',
                                      'lineart': 'lineart',
                                      'face': 'face',
                                      'animated': 'animated'}
        self.async_query = async_query

    def _url_clean_up(self, url):
        """ 
        Some extracted urls can include search parameters after the image file name or can contain complicated encoded redirections.
        This method does its best to clean up image url. After that it just assumes the url is correct and returns it.
        """
        if url!=None and url!="":
            if '?' in url:
                url = url.split('?')[0]
            if '\\' in url:
                url = url.split('\\')[0]
            if '$' in url:
                url = url.split('$')[0]
            # add further filter her is necessary    
        return url
    
    def _fetch_results_from_offset(self, query, result_offset,
                                   aux_params={}, headers={},
                                   num_results=-1):

        image_div_pattern = re.compile(r'class="rg_meta(.*?)</div>')
        image_url_pattern = re.compile(r'"ou":"(.*?)"')

        try:
            page_idx = int(math.floor(result_offset/float(self._results_per_req)))
            page_start = page_idx*self._results_per_req
            page_offset = result_offset - page_start

            # add query position to auxilary parameters
            aux_params['as_q'] = query
            aux_params['ijn'] = page_idx  # ijn is the AJAX page index (0 = first page)

            resp = self.get(GOOGLE_WEB_ENTRY + GOOGLE_WEB_FUNC,
                            params=aux_params, headers=headers)
            resp_str = resp.text

            image_divs = image_div_pattern.findall(resp_str)
            image_data = []
            for div in image_divs:
                image_url_match = image_url_pattern.search(div)
                url = image_url_match.group(1)
                url = self._url_clean_up(url)
                name = url.rsplit('/', 1)[-1]
                if url and name:
                    image_data.append((url, name))

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
        aux_params = {}
        if size:
            aux_params['imgsz'] = size
        if style:
            aux_params['imgtype'] = style

        # prepare shared parameters
        aux_params['tbm'] = 'isch' #image search mode
        aux_params['ijn'] = 0      # causes AJAX request contents only to be returned
            
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}

        # do request
        results = self._fetch_results(query,
                                      num_results,
                                      aux_params=aux_params,
                                      headers=headers)
        
        return results
    
