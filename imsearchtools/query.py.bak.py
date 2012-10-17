#!/usr/bin/env python

"""
Module: image_query
Author: Ken Chatfield <ken@robots.ox.ac.uk>
Created on: 5 Nov 2010

With additions by Kevin McGuinness <kevin.mcguinness@eeng.dcu.ie>

Retrieve ranking lists from various web sources. Currently supported are:

* Google Image Search (using Image Search API - now deprecated)
* Google Image Search (using new Custom Search API)
* Google Image Search (by extracting results directly from the web UI)
* Bing Image Search (using the Bing Image Search API)
* Flickr (using the Flickr API)

Revision History
~~~~~~~~~~~~~~~~
Oct 2012 - Added gevent async support, courtesy of Kevin
Oct 2012 - Added support for Bing, the new Google API and Flickr, updated to new interface
May 2011 - Updated Google web search method due to updates
Nov 2010 - Original version with support for Google Image Search API + scraping
"""

from engines import bing_api *
from engines import google_api *
from engines import google_old_api *
from engines import google_web *
from engines import flickr_api *
    
