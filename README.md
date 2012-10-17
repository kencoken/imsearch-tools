Web Image Downloader Tools
============================================

Author: Ken Chatfield, University of Oxford – <ken@robots.ox.ac.uk>

Copyright 2010-2012, all rights reserved.

Installation Instructions
-------------------------
 + Install the following Python dependencies:
     - `gevent`
     - `restkit`
     - `pil` (Python Imaging Library)
 + Add `imsearchtools` directory to your `PYTHON_PATH`
 + Update `authentication.py` in the `/imsearchtools/engines/api_credentials` directory
   with appropriate API keys for each method (see section below for how to obtain keys)
   
Usage Instructions
------------------

#### 1. Querying web engine for image URLs

    >> import imsearchtools
    >> google_searcher = imsearchtools.query.GoogleWebSearch()
    >> results = google_searcher.query('car')
    >> results
    [{'image_id': 'ANd9GcTfVgJYjlinlqyLfOyUEkPutMMSeyrMErTrTtLDhYCDlTP-4RnKIiQ4knE',
      'url': 'http://asset3.cbsistatic.com/cnwk.1d/i/tim/2012/09/19/35446285_620x433.jpg'},
     {'image_id': 'ANd9GcQGcCEBC2WZlDnPjxDDJ_prdEPYlSWTqAYmIsIFIk7RYvtEmrGPsB5B2NI',
      'url': 'http://asset0.cbsistatic.com/cnwk.1d/i/tim/2012/08/15/35414204_620x433.jpg'},
     … ]
     
Currently the following search services are supported:

 + **GoogleWebSearch( )** – Image search using Google, extracted direct from the web
     - Preferred method for Google Image search
 + **GoogleAPISearch ( )** – Image search using Google, using the *Google Custom Search API*
     - A limit of 100 images per search is imposed
     - The results are different (slightly worse) than when using direct extraction
     - A 'custom search engine' must be created to use the API, with a list of sites to
       search specified during creation. However, selecting 'search these sites + entire
       web' in the options appears to give identical results to those returned by
       `GoogleAPISearch()`
     - Details and authentication key available at:
       <https://developers.google.com/custom-search/v1/overview/>
 + **GoogleOldAPISearch ( )** – Image search using Google, using the *Google Image Search API*
     - The *Google Image Search API* is now deprecated
     - A limit of 64 images per search is imposed
     - There is a higher default limit on number of free requests/day than with the
       new API
     - Details and authentication key available at:
       <https://developers.google.com/image-search/>
 + **BingAPISearch ( )** – Image search using Bing, using the *Bing Search API*
     - Details and authentication key available at:
       <http://www.bing.com/developers/>
 + **FlickrAPISearch ( )** – Image search using Flickr, using the *Flickr API*
     - Provides text search of Flickr photos by associated tags
     - Details and authentication key available at:
       <http://www.flickr.com/services/api/>
       
A test script `query_test.py` is provided which can be used to visualize the difference
between the methods. Run it by issuing:

    $ python query_test.py <query>

#### 2. Downloading retrieved image URLs

Using the `results` array returned by `<web_service>.query(q)`:

    ...
    >> imsearchtools.downimages(results, '/path/to/save/images')
    
Revision History
----------------

 + *Oct 2012* - Added `gevent` async support, courtesy of Kevin
 + *Oct 2012* - Added support for Bing, the new Google API and Flickr, updated to
                new interface
 + *May 2011* - Updated Google web search method due to updates
 + *Nov 2010* - Original version with support for Google Image Search API + scraping
 