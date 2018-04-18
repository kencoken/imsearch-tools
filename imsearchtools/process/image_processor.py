#!/usr/bin/env python

"""
Module: image_processor
Author: Ken Chatfield <ken@robots.ox.ac.uk>
        Kevin McGuinness <kevin.mcguinness@eeng.dcu.ie>
Created on: 19 Oct 2012
"""

import os
import urlparse
import logging
from PIL import Image as PILImage
import imutils

log = logging.getLogger(__name__)

class FilterException(Exception):
    pass


class ImageProcessorSettings(object):
    """
    Settings class for ImageProcessor

    Defines the following setting groups:
    
        filter - settings related to filtering out of images from further processing
        conversion - settings related to the standardization and re-writing of
            downloaded images
        thumbnail - settings related to the generation of thumbnails for downloaded images
    """

    def __init__(self):
        self.filter = dict(min_width=1,
                           min_height=1,
                           max_width=10000,
                           max_height=10000,
                           max_size_bytes=2*4*1024*1024, #2 MP
                           remove_flickr_placeholders=False)

        self.conversion = dict(format='jpg',
                               suffix='-clean',
                               max_width=10000,
                               max_height=10000,
                               subdir='')

        self.thumbnail = dict(format='jpg',
                              suffix='-thumb',
                              subdir='',
                              width=90,
                              height=90,
                              pad_to_size=True)

    
class ImageProcessor(object):
    """
    Base class providing utility methods for cleaning up images downloaded
    from the web. Requires the subclass to define the following:

    Attributes:
        opts - ImageProcessorSettings class containing settings for the image processor
    """

    def __init__(self, opts=ImageProcessorSettings()):
        self.opts = opts

    # Create filenames
    def _filename_from_urldata(self, urldata):
        extension = os.path.splitext(urlparse.urlparse(urldata['url']).path)[1]
        fn = urldata['image_id'] + extension
        return fn

    def _clean_filename_from_filename(self, fn):
        clean_fn = (os.path.splitext(fn)[0] +
                    self.opts.conversion['suffix'] + '.' +
                    self.opts.conversion['format'].lower())
        if self.opts.conversion['subdir']:
            clean_fn = os.path.join(self.opts.conversion['subdir'], clean_fn)
        return clean_fn

    def _thumb_filename_from_filename(self, fn):
        name = os.path.splitext(fn)[0]
        suffix = self.opts.thumbnail['suffix']
        width, height = self.opts.thumbnail['width'], self.opts.thumbnail['height']
        extension = self.opts.thumbnail['format'].lower()
        thumb_fn = '%s%s-%dx%d.%s' % (name, suffix, width, height, extension)
        if self.opts.thumbnail['subdir']:
            thumb_fn = os.path.join(self.opts.thumbnail['subdir'], thumb_fn)
        return thumb_fn

    # Process image and standardize it
    def process_image(self, fn):
        """
        Process a single image, saving a cleaned up version of the image + thumbnail

        Args:
            fn: the filename of the image to process

        Returns:
            A tuple (clean_fn, thumb_fn) containing the filenames of the saved
            cleaned up image and thumbnail
        """
        im = imutils.LazyImage(fn)
        self._filter_image(fn)

        # write converted version
        clean_fn = self._clean_filename_from_filename(fn)
        if not imutils.image_exists(clean_fn):
            if self.opts.filter['remove_flickr_placeholders']:
                self._filter_flickr_placeholder(fn)
            convimg = imutils.downsize_by_max_dims(im.image,
                                                   (self.opts.conversion['max_height'],
                                                    self.opts.conversion['max_width']))
            imutils.save_image(clean_fn, convimg)
        else:
            log.info('Converted image available: %s', clean_fn)

        # write thumbnail
        thumb_fn = self._thumb_filename_from_filename(fn)
        if not imutils.image_exists(thumb_fn):
            thumbnail = imutils.create_thumbnail(im.image,
                                                 (self.opts.thumbnail['height'],
                                                  self.opts.thumbnail['width']))
            imutils.save_image(thumb_fn, thumbnail)
        else:
            log.info('Thumbnail image available: %s', thumb_fn)

        return clean_fn, thumb_fn

    def _filter_image(self, fn):
        # This is faster than reading the full image into memory: the PIL open
        # function is lazy and only reads the header until the data is requested
        im = PILImage.open(fn)
        w, h = im.size
        # This is an in memory size *estimate*
        nbytes = w * h * len(im.mode)

        if w < self.opts.filter['min_width']:
            raise FilterException, 'w < min_width'
        if h < self.opts.filter['min_height']:
            raise FilterException, 'h < min_height'
        if w > self.opts.filter['max_width']:
            raise FilterException, 'w > max_width'
        if h > self.opts.filter['max_height']:
            raise FilterException, 'h > max_height'
        if nbytes > self.opts.filter['max_size_bytes']:
            raise FilterException, 'nbytes > max_size_bytes'

    def _filter_flickr_placeholder(self, fn):
        import hashlib
        with open(fn) as fid:
            if hashlib.sha256(fid.read()).hexdigest() == '0f28f49410a89e24c95acfd345210cc6f2294814584ad7c60f698fee74e46aad':
                raise FilterException, 'Flickr placeholder image filtered'
