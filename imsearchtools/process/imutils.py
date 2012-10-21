#!/usr/bin/env python

"""
Module: imutils
Author: Ken Chatfield <ken@robots.ox.ac.uk>
        Kevin McGuinness <kevin.mcguinness@eeng.dcu.ie>
Created on: 19 Oct 2012
"""

import numpy as np
import skimage.io
import scipy.misc
import math

def image_exists(fn):
    try:
        with open(fn) as f: pass
    except IOError as e:
        return False
    return True

def load_image(fn):
    return skimage.io.imread(fn)

def save_image(fn, im):
    skimage.io.imsave(fn, im)

def create_thumbnail(im, shape=(128,128), pad_to_size=True):
    h, w = im.shape[:2]
    if w > h:
        nw = shape[1]
        nh = int(nw * (h / float(w)))
    else:
        nh = shape[0]
        nw = int(nh * (w / float(h)))
    resized = scipy.misc.imresize(im, (nh, nw))
    if pad_to_size:
        thumbnail = np.zeros(shape + im.shape[2:], dtype=im.dtype)
        cx = int((shape[1] - nw) / 2.0)
        cy = int((shape[0] - nh) / 2.0)
        thumbnail[cy:cy+nh,cx:cx+nw,...] = resized
        return thumbnail
    else:
        return resized

class LazyImage(object):
    def __init__(self, filename):
        self.filename = filename
        self._image = None
    
    @property
    def image(self):
        if self._image is None:
            self._image = load_image(self.filename)
        return self._image
