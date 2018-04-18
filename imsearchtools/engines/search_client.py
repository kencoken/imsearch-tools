#!/usr/bin/env python

import gevent

class QueryException(Exception):
    pass

class NoAPICredentials(Exception):
    pass

## Search Classes
#  --------------------------------------------

class SearchClient(object):
    """
    Base class for all search clients, providing utility methods common
    to all classes. Requires the subclass to define the following:

    PROPERTIES:
     + _supported_sizes_map (Dict)
          mapping of external supported sizes to internal (API) supported sizes
          e.g. {'large': 'xxlarge', 'medium': 'xlarge|large|medium', 'small': 'small'}
     + _supported_styles_map (Dict)
          mapping of external supported styles to internal (API) supported styles
          e.g. {'photo': 'Photo', 'graphics': 'Graphics'}
     + _results_per_req (Integer)
          maximum number of queries to make per request, normally defined by the API
     + async_query (Bool)
          make queries asynchronously or not
     + timeout (Float)
          timeout in seconds for HTTP requests
    METHODS:
     + def _fetch_results_from_offset(self, query, result_offset,
                                      aux_params={}, headers={},
                                      num_results=-1)
          this method should return a set of results given an offset from the
          first result and a count of results to return
    """

    @property
    def supported_sizes(self):
        return self._supported_sizes_map.keys()

    @property
    def supported_styles(self):
        return self._supported_styles_map.keys()

    def _size_to_native_size(self, size):
        if size == '':
            return size
        if size not in self._supported_sizes_map:
            # do not completely abort because of this
            print "**** WARNING: Unsupported size '%s'. Ignoring value. ****" % size
            return ''

        return self._supported_sizes_map[size]

    def _style_to_native_style(self, style):
        if style == '':
            return style
        if style not in self._supported_styles_map:
            # do not completely abort because of this
            print "**** WARNING: Unsupported style '%s'. Ignoring value. ****" % style
            return ''

        return self._supported_styles_map[style]

    def _fetch_results(self, query, num_results,
                       aux_params={},
                       headers={}):
        """Routine for fetching results from server using multiple requests.

        Parameters:
        - query
            the text query
        - num_results
            the number of results to return for this query - may be ignored
        - fetch_results_from_offset_func
            the function to be called to retrieve results for a given subset of results
            should be of the form:
                func(self, query, result_offset[, num_results, aux_params, headers])
        - [aux_params, headers]
            optional parameter/header arguments
        """
        if self.async_query:
            jobs = [gevent.spawn(self._fetch_results_from_offset,
                                 query, result_offset,
                                 aux_params=aux_params,
                                 headers=headers,
                                 num_results=num_results)
                    for result_offset in range(0, num_results, self._results_per_req)]

            gevent.joinall(jobs, timeout=self.timeout)

            results = []

            for job in jobs:
                if job.value:
                    results.extend(job.value)
        else:
            results = []

            for result_offset in range(0, num_results, self._results_per_req):
                results.extend(self._fetch_results_from_offset(query,
                                                               result_offset,
                                                               aux_params=aux_params,
                                                               headers=headers,
                                                               num_results=num_results))

        if not results:
            raise QueryException("No image URLs could be retrieved")

        return results
