#!/usr/bin/env python

import imsearchtools as ist
import time
import sys
import os


# demo callback that simply prints a json object
def test_callback(out_dict):
    import json
    print json.dumps(out_dict)
    #time.sleep(0.2)

# The query string can be specified in the command line
# Otherwise, 'car' is used by default.
if len(sys.argv) < 2:
    test_query_str = 'car'
else:
    test_query_str = sys.argv[1]

# example of querying for image URLs using Google Web engine
searcher = ist.query.GoogleWebSearch()
print 'Executing Google Web Search...'
t = time.time()
results = searcher.query(test_query_str)
print 'Retrieved %d result URLs in %f seconds' % (len(results), (time.time() - t))

# create output directory if necesary
outdir = os.path.join(os.getcwd(), 'demos', 'downloaded_images')
if not os.path.isdir(outdir):
    os.makedirs(outdir)

# example of downloading images from a query engine
imgetter = ist.process.ImageGetter()
print 'Downloading images...'
t = time.time()
# - A demo callback 'test_callback' is provided. If not required, the parameter can simply be removed
# - The boolean 'process_images' determines where the original images should be processed
#   (i.e. cleaned and scaled) after the download. 'False' indicate no processing is required.
#   The default value is 'True'.
output_fns = imgetter.process_urls(results, outdir, test_callback, process_images=False)
print 'Downloaded %d results in %f seconds' % (len(output_fns), (time.time() - t))
