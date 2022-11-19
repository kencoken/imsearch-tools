#!/usr/bin/env python

"""
Module: api_credentials
Author: Ken Chatfield <ken@robots.ox.ac.uk>
Created on: 16 Oct 2012

API credentials for image_query module

Last update:

04 Oct 2016
Added keys exclusive to VGG accounts for BING_API ang GOOGLE_API.
Ernesto Coto

13 Dec 2016
Renamed the BING_API key to BING_API_KEY_V1 to reflect the version number
Added BING_API_KEY_V5 as the key for the new version (v5) of the BING API
Ernesto Coto

"""

## API Credentials
#  --------------------------------------------

# Obtain at:
# https://datamarket.azure.com/dataset/5BA839F1-12CE-4CCE-BF57-A49D98D29A44
BING_API_KEY_V1 = ''
BING_API_KEY_V5 = ''

# Obtain at:
# https://developers.google.com/image-search/
GOOGLE_OLD_API_KEY = ''

# Obtain at:
# https://developers.google.com/custom-search/v1/overview
GOOGLE_API_KEY = ''
GOOGLE_API_CX = ''

# Obtain at:
# http://www.flickr.com/services/api/
FLICKR_API_KEY = ''
FLICKR_API_SECRET = ''
