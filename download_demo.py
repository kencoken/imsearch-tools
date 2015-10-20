#!/usr/bin/env python

import imsearchtools as ist
import time
import sys
import os


def test_callback(out_dict):
    import json
    print json.dumps(out_dict)
    #time.sleep(0.2)

if len(sys.argv) < 2:
    test_query_str = 'car'
else: test_query_str = sys.argv[1]

searcher = ist.query.GoogleWebSearch()
print 'Executing Google Web Search...'
t = time.time()
# example of querying for image URLs using Google Web engine
results = searcher.query(test_query_str)
print 'Retrieved %d result URLs in %f seconds' % (len(results), (time.time() - t))

imgetter = ist.process.ImageGetter()
print 'Downloading images...'
t = time.time()
outdir = os.path.join(os.getcwd(), 'demos', 'downloaded_images')
if not os.path.isdir(outdir):
    os.makedirs(outdir)
# example of downloading images from a query engine
# a demo callback is also provided -
#    if it is not required, the parameter can simply be removed
output_fns = imgetter.process_urls(results, outdir, test_callback)
print 'Downloaded %d results in %f seconds' % (len(output_fns), (time.time() - t))
