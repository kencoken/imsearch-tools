#!/usr/bin/env python

"""Retrieve ranking lists from Google Image search

Uses either the Google AJAX API:
http://code.google.com/apis/imagesearch/v1/
or direct page scraping to retrieve a ranked list of images returned
from Google Image search for a given text query.

Date created: 5 Nov 2010
"""

import urllib, urllib2, math
import simplejson
            
        
    
# API QUERY FUNCTION -----------------------------------------------------------
    
def doapiquery(querytext, imageSize=None, imageType=None, imageFiletype=None):
    '''Execute Google Image search returning list of results.
    
       Performs a Google Image search using the Google AJAX API using query text
       and returns a list of results, with each result being a dictionary
       containing fields as described at:
       http://code.google.com/apis/imagesearch/v1/jsondevguide.html
       
       The optional parameters correspond to the imgsiz, imgtype and as_filetype
       parameters described on the same page, and should be either string inputs
       or 'None' (the default) if the corresponding parameter is not to be
       specified.
        
       Note: currently the AJAX API is limited to retrieving 64 images
       (8 pages of 8 results)'''
    # initialise pages variable with index of 0 to retrieve first results page
    pageidx = 0
    pages = [{"start":"0"}]
    
    # container for concatenated results
    results = [];
    
    # container for extra url input parameters
    extparams = dict()
    
    # search url
    url = 'https://ajax.googleapis.com/ajax/services/search/images'
    
    # add default parameters
    extparams['v'] = '1.0'
    extparams['key'] = 'ABQIAAAAhwuK0v87GeWdUZOHg2LyQRReZB6mFHLdT1tlK9Y2guPDN_lJaxS2tDs5eI-6n02Plk7E7YTfsWgG2w'
    # add any extra parameters
    if imageSize != None:
        extparams['imgsz'] = imageSize
    if imageType != None:
        extparams['imgtype'] = imageType
    if imageFiletype != None:
        extparams['as_filetype'] = imageFiletype
    
    # need to call api recursively to get all possible (pages of) results
    while (pageidx < len(pages)):
        params = {'q' : querytext,
                  'rsz' : '8',
                  'start' : pages[pageidx]["start"]}
        params.update(extparams)
        data = urllib.urlencode(params)
        
        request = urllib2.Request((url + '?' + data), None,
                                  {'Referer':'http://www.robots.ox.ac.uk/~ken'})
        response = urllib2.urlopen(request)
        
        page_results = simplejson.load(response)
        
        results = results + page_results['responseData']['results']
            
        if pageidx == 0:
            pages = page_results['responseData']['cursor']['pages']
        pageidx += 1
    
    return results
    
# WEB EXTRACTOR QUERY FUNCTION -------------------------------------------------

def dowebquery(querytext, imageSize=None, imageType=None, imageFiletype=None, imageCount=63):
    '''Execute Google Image search returning list of results (web extractor version)
       
       Returns the results of a Google image search executed as a user query through
       the standard Google browser interface. A custom extraction engine is used to
       extract the results of the search into a dictionary formatted output similar to
       that produced by doapiquery (via the official Google Image Search API) except
       only the 'results' (image results) section is returned, and for each image
       only the 'unescapedUrl' and 'imageId' fields are returned.
       
       NOTE: the extra parameters do not accept combinations using '|' as with the
       api. Also, the size parameter maps as follows:
           'small' -> 's'
           'medium' and 'large' and 'xlarge' -> 'm'
           'xxlarge' and 'huge' -> 'l'
        
       The extra 'imageCount' parameter sets how many images to return.
       
       This function was coded in December 2010 and worked with the version of
       Google Image search publically available on that date.
       
       Updated: May 2011'''
    IMAGES_PER_PAGE = 21  
        
    # container for concatenated results
    results = [];
    
    
    url = 'http://www.google.com/images'
    
    # construct extra switches input parameter ('tbs')
    extparams = []
    if imageSize != None:
        sizestr = ''
        if imageSize == 'icon': sizestr = 'i'
        elif imageSize == 'small': sizestr = 's'
        elif imageSize == 'medium' or imageSize == 'large' or imageSize == 'xlarge': sizestr = 'm'
        elif imageSize == 'xxlarge' or imageSize == 'huge': sizestr = 'l'
        extparams.append('isz:' + sizestr)
    if imageType != None:
        extparams.append('itp:' + imageType)
    if imageFiletype != None:
        extparams.append('ift:' + imageFiletype)
    extparamsstr = ''
    for i in range(0,len(extparams)):
        extparamsstr = extparamsstr + extparams[i]
        if i != len(extparams)-1:
            extparamsstr = extparamsstr + ','
        
    'itp:photo,isz:m,ift:jpg'
    params = {'q' : querytext}
    if extparamsstr != '':
        params['tbs'] = extparamsstr
    
    # set user agent to ie7 to get simpler (paginated) version of results page
    headers = {'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)'}
    
    numpages = int(math.ceil(imageCount/float(IMAGES_PER_PAGE)))
    
    for page in range(1,numpages+1):
        params['start'] = (page-1)*IMAGES_PER_PAGE+1
        data = urllib.urlencode(params)
        request = urllib2.Request((url + '?' + data), None, headers)
        response = urllib2.urlopen(request)
        
        # print page stats to console
        print '** Processing page ' + str(page) + ' (starting index ' + str(params['start']) + ')'
        print '** Query URL: ' + url + '?' + data
        
#        soup = BeautifulSoup(response.read())
#        
#        for i in range(0,IMAGES_PER_PAGE):
#            imgcontainer = soup.find('td', id=('tDataImage' + str(i)))
#            googlepath = imgcontainer('a')[0]['href']
#            params = parse_qs(googlepath)
#            results.append({'unescapedUrl': params['imgurl']})

        htmlfile = response.read()
        
        #startpat_url = '/imgres?imgurl\\x3d'
        startpat_url = '/imgres?imgurl='
        #endpat_url = '\\x26'
        endpat_url = '&'
        startpat_id = 'tbn:'
        endpat_id = '"'
        last_end = 0
        results_this_page = 0
        # define vars just for purposes of errmsg
        imgurl_start = -1
        imgurl_end = -1
        imgid_start = -1
        imgid_end = -1
        # iterate through file finding image urls
        while True:
            # extract image url
            imgurl_start = htmlfile.find(startpat_url,last_end) + len(startpat_url)
            if (imgurl_start == -1) or (imgurl_start < last_end): break
            imgurl_end = htmlfile.find(endpat_url,imgurl_start)
            if (imgurl_end == -1) or (imgurl_end < imgurl_start): break
            # extract image id
            imgid_start = htmlfile.find(startpat_id,imgurl_end) + len(startpat_id)
            if (imgid_start == -1) or (imgid_start < last_end): break
            imgid_end = htmlfile.find(endpat_id,imgid_start)
            if (imgid_end == -1) or (imgid_end < imgid_start): break
            # set last seen index for next iteration
            last_end = imgid_end
            # print extracted url to console
            print htmlfile[imgurl_start:imgurl_end]
            # append fields to results list
            results.append({'unescapedUrl': htmlfile[imgurl_start:imgurl_end],
                            'imageId': htmlfile[imgid_start:imgid_end]})
            results_this_page = results_this_page + 1
        # check the number of urls received matches the number of images per page
        if results_this_page != IMAGES_PER_PAGE:
            raise SystemError('IMAGES_PER_PAGE=' + str(IMAGES_PER_PAGE) +
                              ' but only ' +str(results_this_page) +
                              ' images could be extracted from the current page.' +
                              ' imgurl_start = ' + str(imgurl_start) + ',' +
                              ' imgurl_end = ' + str(imgurl_end) + ',' +
                              ' imgid_start = ' + str(imgid_start) + ',' +
                              ' imgid_end = ' + str(imgid_end))
            
    
    if len(results) > imageCount:
        results = results[0:imageCount]
    
    return results
