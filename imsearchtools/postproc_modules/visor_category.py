#!/usr/bin/env python

import os
from socket import *
from flask import json
from gevent_zeromq import zmq

import logging
log = logging.getLogger(__name__)

TCP_TERMINATOR = "$$$"
SUCCESS_FIELD = "success"
TCP_TIMEOUT = 86400.00

def callback_func(out_dict, extra_prms=None):
    # connect to VISOR backend service
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect((extra_prms['backend_host'], extra_prms['backend_port']))
    except Error, e:
        print 'Connect failed', str(e)
        raise e

    sock.settimeout(TCP_TIMEOUT)

    # generate feature file path from image file path
    imfn = os.path.basename(out_dict['clean_fn'])
    (featfn, imext) = os.path.splitext(imfn)
    featfn += '.bin'
    featpath = os.path.join(extra_prms['featdir'], featfn)
    # construct VISOR backend function call
    func_in = dict(func=extra_prms['func'],
                   query_id=extra_prms['query_id'],
                   impath=out_dict['clean_fn'],
                   featpath=featpath,
                   from_dataset=0,
		   extra_params=dict())
    request = json.dumps(func_in)
    
    print 'Request to VISOR backend: ' + request
    
    request = request + TCP_TERMINATOR

    # send request to VISOR backend
    sock.send(request)

    response = ""
    while 1:
        try:
            data = sock.recv(1024)
            if not data:
                break
            response += data
        except timeout:
            print 'Socket timeout'
            sock.close()
            
    sock.close()

    # return URL on ZMQ channel if specified in extra_prms
    if 'zmq_impath_return_ch' in extra_prms:
        created_sock = True
        try:
            # either reuse or create new zmq socket
            if 'zmq_impath_return_sock' not in extra_prms:
                # either reuse or create new zmq context
                # (to create socket)
                if 'zmq_context' in extra_prms:
                    log.info('Reusing ZMQ_CONTEXT')
                    context = extra_prms['zmq_context']
                else:
                    log.info('Generating new ZMQ_CONTEXT')
                    context = zmq.Context()

                impath_sender = context.socket(zmq.REQ)
                impath_sender.connect(extra_prms['zmq_impath_return_ch'])
            else:
                created_sock = False
                log.info('Reusing ZMQ_SOCKET')
                impath_sender = extra_prms['zmq_impath_return_sock']

            impath_sender.send(str(out_dict['clean_fn']))
            impath_sender.recv()
            log.info('Completed request')

        finally:
            if created_sock: impath_sender.close()
