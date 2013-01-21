#!/usr/bin/env python

import os

from flask import Flask, request, Response, url_for
from gevent.wsgi import WSGIServer
from flask import json

from imsearchtools import query as image_query
from imsearchtools import process as image_process
from imsearchtools import postproc_modules

SERVER_PORT = 8150

app = Flask(__name__)
app.debug = True


def imsearch_query(query, engine, query_params):
    if engine == 'bing_api':
        searcher = image_query.BingAPISearch()
    elif engine == 'google_old_api':
        searcher = image_query.GoogleOldAPISearch()
    elif engine == 'google_api':
        searcher = image_query.GoogleAPISearch()
    elif engine == 'google_web':
        searcher = image_query.GoogleWebSearch()
    elif engine == 'flickr_api':
        searcher = image_query.FlickrAPISearch()
    else:
        raise ValueError('Unkown query engine')

    return searcher.query(query, **query_params)

def imsearch_download_to_static(query_res_list, postproc_module=None):
    imgetter = image_process.ImageGetter()
    outdir = os.path.join(os.getcwd(), 'static')
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    # if a postprocessing module is defined, find the callback function
    # of the module
    if postproc_module:
        callback_func = postproc_modules.get_module_callback(postproc_module)
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

@app.route('/')
def index():
    return "imsearch HTTP service is running"

@app.route('/query')
def query():
    # parse GET args
    query = request.args['q']
    engine = request.args.get('engine', 'bing_api')

    query_params = dict()
    for param_nm in ['size', 'style', 'num_results']:
        if param_nm in request.args:
            query_params[param_nm] = request.args[param_nm]
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

@app.route('/exec_pipeline', methods=['POST'])
def exec_pipeline():
    # parse POST form args
    query = request.form['q']
    engine = request.form.get('engine', 'bing_api')
    postproc_module = request.form.get('postproc_module', None) # default to no postproc module
    # < default to returning list only if not using postproc module >
    return_dfiles_list = request.form.get('return_dfiles_list', (postproc_module == None))
    return_dfiles_list = (int(return_dfiles_list) == 1)

    query_params = dict()
    for param_nm in ['size', 'style', 'num_results']:
        if param_nm in request.form:
            query_params[param_nm] = request.form[param_nm]
    # execute query
    query_res_list = imsearch_query(query, engine, query_params)
    #query_res_list = query_res_list[:5] # DEBUG CODE
    # download images
    dfiles_list = imsearch_download_to_static(query_res_list, postproc_module)
    # convert pathnames to URL paths
    url_dfiles_list = make_url_dfiles_list(dfiles_list)

    if return_dfiles_list:
        return Response(json.dumps(url_dfiles_list), mimetype='application/json')
    else:
        return 'DONE'

if __name__ == '__main__':
    http_server = WSGIServer(('', SERVER_PORT), app)
    http_server.serve_forever()
    
