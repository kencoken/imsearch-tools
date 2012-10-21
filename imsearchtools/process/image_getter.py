#!/usr/bin/env python

"""
Module: image_getter
Author: Ken Chatfield <ken@robots.ox.ac.uk>
        Kevin McGuinness <kevin.mcguinness@eeng.dcu.ie>
Created on: 19 Oct 2012
"""

import gevent
import restkit
import os
import urlparse

from image_processor import *
import imutils

import logging

from callback_handler import CallbackHandler

#logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class ImageGetter(ImageProcessor):
    """Class for downloading cleaned-up images from the web, given a set of URLs

    The class should be initialized with an instance of ImageProcessorSettings() to
    define conversion options. Following this, a set of results returned from a
    image search client class can be processed by calling `process_urls` with
    the dictionary returned from the image search.

    Cleaned-up versions of the image, along with thumbnails, will be output.
    """

    def __init__(self, timeout=5.0, opts=ImageProcessorSettings()):
        self.opts = opts
        self.timeout = timeout
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.subprocs = []

    def process_url(self, urldata, output_dir, call_completion_func=False):
        error_occurred = False
        try:
            output_fn = os.path.join(output_dir, self._filename_from_urldata(urldata))
            self._download_image(urldata['url'], output_fn)
            clean_fn, thumb_fn = self.process_image(output_fn)
        except restkit.errors.RequestError, e:
            log.info('Request exception for %s (%s)', urldata['url'], str(e))
            error_occurred = True
        except IOError, e:
            log.info('IO Error for: %s (%s)', urldata['url'], str(e))
            error_occurred = True
        except FilterException, e:
            log.info('Filtered out: %s (%s)', urldata['url'], str(e))
            error_occurred = True

        if not error_occurred:
            out_dict = urldata
            out_dict['orig_fn'] = output_fn
            out_dict['clean_fn'] = clean_fn
            out_dict['thumb_fn'] = thumb_fn

            if call_completion_func:
                # use callback handler to run completion func configured in process_urls
                self._callback_handler.run_callback(out_dict)

            return out_dict
        else:
            if call_completion_func:
                # indicate to callback handler that a URL to be processed failed
                self._callback_handler.skip()

            return None
        
    def _download_image(self, url, output_fn):
        if imutils.image_exists(output_fn):
            log.info('Output filename exists for URL: %s', url)
            return

        log.info('Downloading URL: %s', url)
        resp = restkit.request(url, headers=self.headers)
        
        with resp.body_stream() as body:
            with open(output_fn, "wb") as f:
                for block in body:
                    f.write(block)
        
    def process_urls(self, urls, output_dir, completion_func=None,
                     completion_worker_count=-1):
        """Process returned list of URL dicts returned from search client class

        Args:
            urls: a dictionary of URLs returned from a search client class
                of the form: [{'url': <>, 'image_id': <>, 'title': <>}, ...]
            output_dir: the directory in which output images should be stored
            [completion_func]: an optional callback made immediately after each
                image has been downloaded - should be of the form:
                    f(out_dict)
                where out_dict is a dictionary of the same form as a single
                entry in the return dict (i.e. containing 'orig_fn', 'clean_fn',
                and 'thumb_fn' fields)

            Returns:
                A list of dictionaries of the form:
                [{'orig_fn':'/path/to/image/as/downloaded/directly/from/url',
                  'clean_fn':'/path/to/processed/and/validated/image',
                  'thumb_fn':'/path/to/thumbnail'},
                  ...]
            
        """

        # prepare workers for callback if using callback function
        # returned process will end once all callbacks have been completed
        if completion_func:
            self._callback_handler = CallbackHandler(completion_func,
                                                     len(urls),
                                                     completion_worker_count)

        # launch main URL processor jobs
        jobs = [gevent.spawn(self.process_url,
                             urldata, output_dir,
                             call_completion_func=(completion_func is not None))
                for urldata in urls]

        # wait for all URL processor jobs to complete
        gevent.joinall(jobs, timeout=self.timeout)

        # if using callbacks, wait for all callbacks to complete before continuing
        if completion_func:
            self._callback_handler.join()

        # construct return list of filenames
        results = []

        for job in jobs:
            if job.value:
                results.append(job.value)

        return results
        

