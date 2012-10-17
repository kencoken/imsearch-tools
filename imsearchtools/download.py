#!/usr/bin/env python

"""
Module: image_download
Author: Ken Chatfield <ken@robots.ox.ac.uk>
Created on: 5 Nov 2010

Module for downloading images from search services provided by the
image_query module
"""

import socket, urllib2
import os
import Image
from multiprocessing import Pool

class ImageExtfindError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# PRIVATE FUNCTIONS ------------------------------------------------------------

def __downloadURL(urldata, timeout=5):
    '''Download URLs to file.
    
       Given an input URL/filename tuple, download the given URL to the file
       specified by filename. '''
    
    try:
        # skip if output file already exists
        if os.path.exists(urldata['filename']) == False:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent','Mozilla/5.0')] # pretend to be firefox
            img = opener.open(urldata['url'], None, timeout)
            
            file = open(urldata['filename'], 'wb')
            file.write(img.read())
            file.close()
            
        # open image in order to verify downloaded image is valid
        im = Image.open(urldata['filename'])
        
        # now see if a valid extension has been specified (required)
        unused_root, fileext = os.path.splitext(urldata['filename'])
        if (fileext == '') or (fileext.find('?') != -1):
            # if there is no valid extension supplied, then try to extract
            # this using the loaded image...
            imformat = im.format
            if imformat != None:
                impath = urldata['filename'] + '.' + imformat.lower()
                os.rename(urldata['filename'], impath)
            else:
                raise ImageExtfindError(urldata['filename'])
        else:
            impath = urldata['filename']
        
        # finally, store downloaded image in status arrays
        print 'downloaded: ' + impath
        if urldata['status'] != None:
            urldata['status'].localTrainImages = urldata['status'].localTrainImages + [impath,]
            urldata['status'].featComputed = [False]*len(urldata['status'].localTrainImages)

    except urllib2.URLError:
        # ignore errors (just skip to next result without downloading)
        print 'skipping... urllib2.URLError raised'
    except socket.error:
        print 'skipping... socket.error raised'
    except IOError:
        print 'skipping... downloaded image was corrupt'
        if os.path.exists(urldata['filename']):
            os.remove(urldata['filename'])
    except ImageExtfindError:
        print 'skipping... valid image extension could not be extracted'
        if os.path.exists(urldata['filename']):
            os.remove(urldata['filename'])

# IMAGE DOWNLOAD FUNCTIONS -----------------------------------------------------

def downimages(response, path, workers=10, status=None):
    '''Download image results of a Google Image search (multiple processes).
    
       Downloads the images specified by the structure returned from a call to
       'doapiquery()'. 'path' specifies where to save the images. This version uses
       multiple processes to download several images in parallel.'''
    if os.path.isdir(path) == False:
        os.makedirs(path,0755)
    
    urldata = []
    for result in response:
        unused_fileroot, fileext = os.path.splitext(result['url'])
        filename = result['image_id'] + fileext
        filename = os.path.join(path,filename)
        urldata.append({'url': result['url'],
                        'filename': filename,
                        'status': status})  # this seems a bit hacky, but works
    
    p = Pool(workers)
    p.map(__downloadURL, urldata)
    print 'Finished downloading images'

