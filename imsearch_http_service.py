#!/usr/bin/env python

import os

from flask import Flask, request, Response, url_for
from gevent.wsgi import WSGIServer
from flask import json

from imsearchtools import query as image_query
from imsearchtools import process as image_process
from imsearchtools import postproc_modules

import logging
logging.basicConfig()

SERVER_PORT = 8150
SUPPORTED_ENGINES = ['bing_api', 'google_old_api', 'google_api', 'google_web', 'flickr_api']

app = Flask(__name__)
app.debug = True


def imsearch_query(query, engine, query_params, query_timeout=-1.0):
    # prepare input arguments for searcher initialization if non-default
    searcher_args = dict()
    if query_timeout > 0.0:
        searcher_args['timeout'] = query_timeout
    # initialize searcher
    if engine == 'bing_api':
        searcher = image_query.BingAPISearch(**searcher_args)
    elif engine == 'google_old_api':
        searcher = image_query.GoogleOldAPISearch(**searcher_args)
    elif engine == 'google_api':
        searcher = image_query.GoogleAPISearch(**searcher_args)
    elif engine == 'google_web':
        searcher = image_query.GoogleWebSearch(**searcher_args)
    elif engine == 'flickr_api':
        searcher = image_query.FlickrAPISearch(**searcher_args)
    else:
        raise ValueError('Unkown query engine')
    # execute the query
    return searcher.query(query, **query_params)

def imsearch_download_to_static(query_res_list, postproc_module=None,
                                postproc_extra_prms=None,
                                custom_local_path=None,
                                imgetter_params=None):
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

    # if a postprocessing module is defined, find the callback function
    # of the module
    if postproc_module:
        callback_func = postproc_modules.get_module_callback(postproc_module)
        if postproc_extra_prms:
            return imgetter.process_urls(query_res_list, outdir, callback_func,
                                         completion_extra_prms=postproc_extra_prms)
        else:
            return imgetter.process_urls(query_res_list, outdir, callback_func)
    else:
        return imgetter.process_urls(query_res_list, outdir)

def make_url_dfiles_list(dfiles_list):
    cwd = os.getcwd()
    # recast local fs image paths as server paths using hostname from request
    for dfile_ifo in dfiles_list:
        dfile_ifo['orig_fn'] = 'http://' + request.host + dfile_ifo['orig_fn'].replace(cwd, '')
        dfile_ifo['thumb_fn'] = 'http://' + request.host + dfile_ifo['thumb_fn'].replace(cwd, '')
        dfile_ifo['clean_fn'] = 'http://' + request.host + dfile_ifo['clean_fn'].replace(cwd, '')
    return dfiles_list

def test_func():
    import time
    time.sleep(5.0)

@app.route('/callback_test')
def callback_test():
    cbhandler = image_process.CallbackHandler(test_func, 100, 50)
    for i in range(0,100):
        cbhandler.run_callback()
    print 'Done launching callbacks!'
    cbhandler.join()
    return 'Done!'

@app.route('/')
def index():
    return "imsearch HTTP service is running"

@app.route('/query')
def query():
    # parse GET args
    query = request.args['q']
    engine = request.args.get('engine', 'google_web')

    query_params = dict()
    for param_nm in ['size', 'style']:
        if param_nm in request.args:
            query_params[param_nm] = request.args[param_nm]
    if 'num_results' in request.args:
        query_params['num_results'] = int(request.args['num_results'])
    # execute query
    query_res_list = imsearch_query(query, engine, query_params)
    
    return Response(json.dumps(query_res_list), mimetype='application/json')

@app.route('/download', methods=['POST'])
def download():
    # parse POST data
    query_res_list = request.json
    if not query_res_list:
        raise ValueError("Input must be 'application/json' encoded list of urls")
    # download images
    dfiles_list = imsearch_download_to_static(query_res_list)
    # convert pathnames to URL paths
    url_dfiles_list = make_url_dfiles_list(dfiles_list)
    
    return Response(json.dumps(url_dfiles_list), mimetype='application/json')

@app.route('/get_postproc_module_list')
def get_postproc_module_list():
    return json.dumps(postproc_modules.get_module_list())

@app.route('/get_engine_list')
def get_engine_list():
    return json.dumps(SUPPORTED_ENGINES)

@app.route('/exec_pipeline', methods=['POST'])
def exec_pipeline():
    # parse POST form args
    query = request.form['q']
    engine = request.form.get('engine', 'google_web')
    postproc_module = request.form.get('postproc_module', None) # default to no postproc module
    postproc_extra_prms = request.form.get('postproc_extra_prms', None)
    if postproc_extra_prms:
        postproc_extra_prms = json.loads(postproc_extra_prms)
    custom_local_path = request.form.get('custom_local_path', None)
    # < default to returning list only if not using postproc module >
    return_dfiles_list = request.form.get('return_dfiles_list', (postproc_module == None))
    return_dfiles_list = (int(return_dfiles_list) == 1)

    # prepare query params
    query_timeout = request.form.get('query_timeout', -1.0)
    query_timeout = float(query_timeout)
    query_params = dict()
    for param_nm in ['size', 'style']:
        if param_nm in request.form:
            query_params[param_nm] = request.form[param_nm]
    if 'num_results' in request.form:
        query_params['num_results'] = int(request.form['num_results'])
    # execute query
    query_res_list = imsearch_query(query, engine, query_params, query_timeout)
    print 'Query for %s completed: %d results retrieved' % (query, len(query_res_list))
    #query_res_list = query_res_list[:5] # DEBUG CODE
    # prepare download params
    imgetter_params = dict()
    for param_nm in ['improc_timeout', 'per_image_timeout']:
        if param_nm in request.form:
            imgetter_params[param_nm] = float(request.form[param_nm])
    for param_nm in ['resize_width', 'resize_height']:
        if param_nm in request.form:
            imgetter_params[param_nm] = int(request.form[param_nm])
    # download images
    print 'Downloading for %s started: %d sec improc_timeout, %d sec per_image_timeout' % (query,
                                                                                           imgetter_params['improc_timeout'] if imgetter_params['improc_timeout'] else -1,
                                                                                           imgetter_params['per_image_timeout'] if imgetter_params['per_image_timeout'] else -1)
    dfiles_list = imsearch_download_to_static(query_res_list, postproc_module,
                                              postproc_extra_prms,
                                              custom_local_path,
                                              imgetter_params)
    print 'Downloading for %s completed: %d images retrieved' % (query, len(dfiles_list))
    # convert pathnames to URL paths (if not running locally and specifying
    # a custom path)
    if not custom_local_path:
        dfiles_list = make_url_dfiles_list(dfiles_list)

    if return_dfiles_list:
        return Response(json.dumps(dfiles_list), mimetype='application/json')
    else:
        return 'DONE'

if __name__ == '__main__':
    http_server = WSGIServer(('', SERVER_PORT), app)
    http_server.serve_forever()
    
