#!/usr/bin/env python

import sys
import logging
#logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

from flask import Flask, request, Response
from flask import json
from gevent.wsgi import WSGIServer
from imsearchtools import http_service_helper

DEFAULT_SERVER_PORT = 8157

zmq_context = None # used to store zmq context created by init_zmq_context function

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return "imsearch HTTP service is running"

@app.route('/callback_test')
def callback_test():
    http_service_helper.test_callback()
    return 'Done!'

@app.route('/query')
def query():
    # parse GET args
    query_text = request.args['q']

    query_params = dict()
    for param_nm in ['size', 'style']:
        if param_nm in request.args:
            query_params[param_nm] = request.args[param_nm]
    if 'num_results' in request.args:
        query_params['num_results'] = int(request.args['num_results'])

    # execute query
    query_res_list = http_service_helper.imsearch_query(query_text, query_params)
    return Response(json.dumps(query_res_list), mimetype='application/json')

@app.route('/download', methods=['POST'])
def download():
    # parse POST data
    query_res_list = request.json
    if not query_res_list:
        raise ValueError("Input must be 'application/json' encoded list of urls")
    # download images
    dfiles_list = http_service_helper.imsearch_download_to_static(query_res_list)
    # convert pathnames to URL paths
    url_dfiles_list = http_service_helper.make_url_dfiles_list(dfiles_list)

    return Response(json.dumps(url_dfiles_list), mimetype='application/json')

@app.route('/get_postproc_module_list')
def get_postproc_module_list():
    return json.dumps(http_service_helper.get_postproc_modules())

@app.route('/init_zmq_context')
def init_zmq_context():
    global zmq_context
    if not zmq_context:
        import zmq
        zmq_context = zmq.Context()
    return 'Success'

@app.route('/exec_pipeline', methods=['POST'])
def exec_pipeline():
    # parse POST form args
    query_text = request.form['q']
    postproc_module = request.form.get('postproc_module', None) # default to no postproc module
    postproc_extra_prms = request.form.get('postproc_extra_prms', None)
    if postproc_extra_prms:
        postproc_extra_prms = json.loads(postproc_extra_prms)
    custom_local_path = request.form.get('custom_local_path', None)
    # < default to returning list only if not using postproc module >
    return_dfiles_list = request.form.get('return_dfiles_list', (postproc_module is None))
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
    query_res_list = http_service_helper.imsearch_query(query_text, query_params, query_timeout)
    print ('Query for %s completed: %d results retrieved' % (query_text, len(query_res_list)))
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
    print ('Downloading for %s started: %d sec improc_timeout, %d sec per_image_timeout' % (query_text,
                                                                                           imgetter_params['improc_timeout'] if imgetter_params['improc_timeout'] else -1,
                                                                                           imgetter_params['per_image_timeout'] if imgetter_params['per_image_timeout'] else -1))
    dfiles_list = http_service_helper.imsearch_download_to_static(query_res_list,
                                                                  postproc_module,
                                                                  postproc_extra_prms,
                                                                  custom_local_path,
                                                                  imgetter_params,
                                                                  zmq_context)
    print ('Downloading for %s completed: %d images retrieved' % (query_text, len(dfiles_list)))
    # convert pathnames to URL paths (if not running locally and specifying
    # a custom path)
    if not custom_local_path:
        dfiles_list = http_service_helper.make_url_dfiles_list(dfiles_list)

    if return_dfiles_list:
        return Response(json.dumps(dfiles_list), mimetype='application/json')

    return 'DONE'


if __name__ == '__main__':
    if len(sys.argv) > 1:
        SERVER_PORT = int(sys.argv[1])
    else:
        SERVER_PORT = DEFAULT_SERVER_PORT
    print ("Starting imsearch_http_service on port", SERVER_PORT)
    http_server = WSGIServer(('', SERVER_PORT), app)
    http_server.serve_forever()

