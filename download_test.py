#!/usr/bin/env python

import imsearchtools as ist
import time
import sys
import os

if len(sys.argv) < 2:
    test_query_str = 'car'
else: test_query_str = sys.argv[1]

searcher = ist.query.GoogleWebSearch()
print 'Executing Google Web Search...'
t = time.time()
results = searcher.query(test_query_str)
print 'Retrieved %d results in %f seconds' % (len(results), (time.time() - t))

imgetter = ist.process.ImageGetter()
print 'Downloading images...'
t = time.time()
outdir = os.path.join(os.getcwd(), 'demos', 'downloaded_images')
if not os.path.isdir(outdir):
    os.makedirs(outdir)
output_fns = imgetter.process_urls(results, outdir)
print 'Retrieved %d results in %f seconds' % (len(output_fns), (time.time() - t))

