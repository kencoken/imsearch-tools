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
    """

    def _size_to_native_size(self, size, supported_sizes_map):
        if size == '':
            return size
        if size not in supported_sizes_map:
            raise ValueError("Unsupported size '%s'" % size)
        else:
            return supported_sizes_map[size]

    def _style_to_native_style(self, style, supported_styles_map):
        if style == '':
            return style
        if style not in supported_styles_map:
            raise ValueError("Unsupported style '%s'" % style)
        else:
            return supported_styles_map[style]
    
    def _fetch_results(self, query, num_results, results_per_req,
                       fetch_results_from_offset_func,
                       aux_params={},
                       headers={},
                       async_query=True):
        """Routine for fetching results from server using multiple requests.

        Parameters:
        - query
            the text query
        - num_results
            the number of results to return for this query
        - results_per_req
            the number of results to return for general requests (from class property)
        - fetch_results_from_offset_func
            the function to be called to retrieve results for a given subset of results
            should be of the form:
                func(self, query, result_offset[, num_results, aux_params, headers])
        - [aux_params, headers]
            optional parameter/header arguments
        - [async_query=True]
            perform function asynchronously or not
        """
        if async_query:
            jobs = [gevent.spawn(fetch_results_from_offset_func,
                                 query, result_offset,
                                 aux_params=aux_params,
                                 headers=headers,
                                 num_results=num_results)
                    for result_offset in range(0, num_results, results_per_req)]

            gevent.joinall(jobs, timeout=self.timeout)

            results = []

            for job in jobs:
                if job.value:
                    results.extend(job.value)
        else:
            results = []

            for result_offset in range(0, num_results, results_per_req):
                results.extend(fetch_results_from_offset_func(query,
                                                              result_offset,
                                                              aux_params=aux_params,
                                                              headers=headers,
                                                              num_results=num_results))
        
        return results
