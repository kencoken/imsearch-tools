#!/usr/bin/env python

"""
Module: imutils
Author: Ken Chatfield <ken@robots.ox.ac.uk>
        Kevin McGuinness <kevin.mcguinness@eeng.dcu.ie>
Created on: 19 Oct 2012
"""

from PIL import Image as PILImage
import math

def image_exists(fn):
    try:
        with open(fn) as f: pass
    except IOError as e:
        return False
    return True

def load_image(fn):
    im = PILImage.open(fn)
    if im.mode != "RGB":
        im = im.convert("RGB")
    return im

def save_image(fn, im):
    im.save(fn)

def downsize_by_max_dims(im, shape=(10000,10000)):
    w, h = im.size
    sf = 1.0
    if h > shape[0]:
        sf = float(shape[0])/h
    if w > shape[1]:
        sf2 = float(shape[1])/w
        if sf2 < sf:
            sf = sf2
    if sf < 1.0:
        resized = im.resize((int(sf*w), int(sf*h)), PILImage.ANTIALIAS)
        return resized
    else:
        return im

def create_thumbnail(im, shape=(128,128), pad_to_size=True):
    resized = downsize_by_max_dims(im, shape)
    nw, nh = im.size
    resized = im.resize((nw, nh), PILImage.ANTIALIAS)
    if pad_to_size:
        thumbnail = PILImage.new('RGB', shape)
        cx = int((shape[1] - nw) / 2.0)
        cy = int((shape[0] - nh) / 2.0)
        thumbnail.paste(resized, (cy,cx))
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
