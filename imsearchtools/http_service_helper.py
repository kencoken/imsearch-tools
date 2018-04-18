#!/usr/bin/env python

import os

from flask import request

from imsearchtools import query as image_query
from imsearchtools import process as image_process
from imsearchtools import postproc_modules


def imsearch_query(query, query_params, query_timeout=-1.0, engine='google_web'):
    # prepare input arguments for searcher initialization if non-default
    searcher_args = dict()
    if query_timeout > 0.0:
        searcher_args['timeout'] = query_timeout
    # initialize searcher
    if engine == 'google_web':
        searcher = image_query.GoogleWebSearch(**searcher_args)
    else:
        raise ValueError('Unkown query engine')
    # execute the query
    return searcher.query(query, **query_params)

def imsearch_download_to_static(query_res_list, postproc_module=None,
                                postproc_extra_prms=None,
                                custom_local_path=None,
                                imgetter_params=None,
                                zmq_context=None):
    # prepare extra parameters if required
    ig_params = dict()
    if imgetter_params:
        if 'improc_timeout' in imgetter_params and imgetter_params['improc_timeout'] > 0.0:
            ig_params['timeout'] = imgetter_params['improc_timeout']
        if 'per_image_timeout' in imgetter_params and imgetter_params['per_image_timeout'] > 0.0:
            ig_params['image_timeout'] = imgetter_params['per_image_timeout']
        do_width_resize = ('resize_width' in imgetter_params and imgetter_params['resize_width'] > 0)
        do_height_resize = ('resize_height' in imgetter_params and imgetter_params['resize_height'] > 0)
        if do_width_resize or do_height_resize:
            improc_settings = image_process.ImageProcessorSettings()
            if do_width_resize:
                improc_settings.conversion['max_width'] = imgetter_params['resize_width']
            if do_height_resize:
                improc_settings.conversion['max_height'] = imgetter_params['resize_height']
            ig_params['opts'] = improc_settings

    imgetter = image_process.ImageGetter(**ig_params)
        
    if not custom_local_path:
        outdir = os.path.join(os.getcwd(), 'static')
    else:
        outdir = custom_local_path
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    # add zmq context and socket as extra parameter if required
    if type(postproc_extra_prms) is not dict:
        postproc_extra_prms = {}

    if zmq_context:
        postproc_extra_prms['zmq_context'] = zmq_context
    # *** pre-creating a connection seems to cause the gevent threads to hang on joining so disable for now ***
    #if 'zmq_impath_return_ch' in postproc_extra_prms and 'zmq_context' in postproc_extra_prms
    #    import zmq
    #    context = postproc_extra_prms['zmq_context']
    #    postproc_extra_prms['zmq_impath_return_sock'] = context.socket(zmq.REQ)
    #    postproc_extra_prms['zmq_impath_return_sock'].connect(postproc_extra_prms['zmq_impath_return_ch'])

    # if a postprocessing module is defined, find the callback function
    # of the module
    if postproc_module:
        callback_func = postproc_modules.get_module_callback(postproc_module)
        if postproc_extra_prms:
            return imgetter.process_urls(query_res_list, outdir, callback_func,
                                         completion_extra_prms=postproc_extra_prms)

        return imgetter.process_urls(query_res_list, outdir, callback_func)

    return imgetter.process_urls(query_res_list, outdir)

def make_url_dfiles_list(dfiles_list):
    cwd = os.getcwd()
    # recast local fs image paths as server paths using hostname from request
    for dfile_ifo in dfiles_list:
        dfile_ifo['orig_fn'] = 'http://' + request.host + dfile_ifo['orig_fn'].replace(cwd, '')
        dfile_ifo['thumb_fn'] = 'http://' + request.host + dfile_ifo['thumb_fn'].replace(cwd, '')
        dfile_ifo['clean_fn'] = 'http://' + request.host + dfile_ifo['clean_fn'].replace(cwd, '')
    return dfiles_list

def get_postproc_modules():
    return postproc_modules.get_module_list()

def test_callback():
    cbhandler = image_process.CallbackHandler(test_func, 100, 50)
    for i in range(0, 100):
        cbhandler.run_callback()
    print 'Done launching callbacks!'
    cbhandler.join()
    print 'Done joining callbacks'

def test_func():
    import time
    time.sleep(5.0)
