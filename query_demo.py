#!/usr/bin/env python

from imsearchtools import query as image_query
from imsearchtools.utils import result_page_gen
import time
import sys
import os

if len(sys.argv) < 2:
    test_query_str = 'car'
else: test_query_str = sys.argv[1]

outdir = os.path.join(os.getcwd(), 'demos')
if not os.path.isdir(outdir):
    os.makedirs(outdir)

test_bing_api = True
test_google_old_api = True
test_google_api = True
test_google_web = True
test_flickr_api = True

num_results = 100

display_results = True

all_results = []
all_generator_names = []

if test_bing_api:
    bing_api_searcher = image_query.BingAPISearch()
    print 'Executing Bing API Search...'
    t = time.time()
    bing_api_results = bing_api_searcher.query(test_query_str,
                                               num_results=num_results)
    bing_api_timing = time.time() - t
    print 'Retrieved %d results in %f seconds' % (len(bing_api_results), bing_api_timing)

    result_page_gen.gen_results_page(bing_api_results,
                                     'BingAPISearch()',
                                     os.path.join(outdir, 'bing_api_results.html'),
                                     show_in_browser=False)

    all_results.append(bing_api_results)
    all_generator_names.append('BingAPISearch()')

if test_google_old_api:
    google_old_api_searcher = image_query.GoogleOldAPISearch()
    print 'Executing Google API Search (Old)...'
    t = time.time()
    google_old_api_results = google_old_api_searcher.query(test_query_str,
                                                           num_results=num_results)
    google_old_api_timing = time.time() - t
    print 'Retrieved %d results in %f seconds' % (len(google_old_api_results), google_old_api_timing)

    result_page_gen.gen_results_page(google_old_api_results,
                                     'GoogleOldAPISearch()',
                                     os.path.join(outdir, 'google_old_api_results.html'),
                                     show_in_browser=False)

    all_results.append(google_old_api_results)
    all_generator_names.append('GoogleOldAPISearch()')

if test_google_api:
    google_api_searcher = image_query.GoogleAPISearch()
    print 'Executing Google API Search (Custom Search)...'
    t = time.time()
    google_api_results = google_api_searcher.query(test_query_str,
                                                   num_results=num_results)
    google_api_timing = time.time() - t
    print 'Retrieved %d results in %f seconds' % (len(google_api_results), google_api_timing)

    result_page_gen.gen_results_page(google_api_results,
                                     'GoogleAPISearch()',
                                     os.path.join(outdir, 'google_api_results.html'),
                                     show_in_browser=False)

    all_results.append(google_api_results)
    all_generator_names.append('GoogleAPISearch()')

if test_google_web:
    google_web_searcher = image_query.GoogleWebSearch()
    print 'Executing Google Web Search...'
    t = time.time()
    google_web_results = google_web_searcher.query(test_query_str,
                                                   num_results=num_results)
    google_web_timing = time.time() - t
    print 'Retrieved %d results in %f seconds' % (len(google_web_results), google_web_timing)

    result_page_gen.gen_results_page(google_web_results,
                                     'GoogleWebSearch()',
                                     os.path.join(outdir, 'google_web_results.html'),
                                     show_in_browser=False)

    all_results.append(google_web_results)
    all_generator_names.append('GoogleWebSearch()')


if test_flickr_api:
    flickr_api_searcher = image_query.FlickrAPISearch()
    print 'Executing Flickr API Search...'
    t = time.time()
    flickr_api_results = flickr_api_searcher.query(test_query_str,
                                                   num_results=num_results)
    flickr_api_timing = time.time() - t
    print 'Retrieved %d results in %f seconds' % (len(flickr_api_results), flickr_api_timing)

    result_page_gen.gen_results_page(flickr_api_results,
                                     'FlickrApiSearch()',
                                     os.path.join(outdir, 'flickr_api_results.html'),
                                     show_in_browser=False)

    all_results.append(flickr_api_results)
    all_generator_names.append('FlickrAPISearch()')

if display_results:
    result_page_gen.combine_results_pages(all_results, all_generator_names,
                                          os.path.join(outdir, 'combined_results.html'))
