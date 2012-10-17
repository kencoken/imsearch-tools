#!/usr/bin/env python

import gevent

## Search Classes
#  --------------------------------------------

class SearchClient(object):
    """Base class for search clients providing some utility methods for
    converting input properties to the internal property names required
    for the current search type using a map, which should be provided by
    the subclass and be of the form e.g. for styles:

        {'photo': 'Photo',
         'graphics': 'Graphics'} <-- LHS external property name, RHS internal name

    Relies on the subclass having the properties:
    - _supported_sizes_map
    - _supported_styles_map
    """

    def _size_to_native_size(self, size):
        if size == '':
            return size
        if size not in self._supported_sizes_map:
            raise ValueError("Unsupported size '%s'" % size)
        else:
            return self._supported_sizes_map[size]

    def _style_to_native_style(self, style):
        if style == '':
            return style
        if style not in self._supported_styles_map:
            raise ValueError("Unsupported style '%s'" % style)
        else:
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

        Relies on the following parameters being defined in the subclass:
        - _results_per_req
            number of results to return for generic requests to the server
        - async_query
            perform function asynchronously or not
        - timeout
            timeout of each request in seconds

        And the following function being defined in the class:
          def _fetch_results_from_offset(self, query, result_offset,
                                         aux_params={}, headers={},
                                         num_results=-1)
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
        
        return results
