#!/usr/bin/env python

from socket import *
from flask import json
from gevent_zeromq import zmq

TCP_TERMINATOR = "$$$"
SUCCESS_FIELD = "success"
TCP_TIMEOUT = 86400.00

def callback_func(out_dict, extra_prms=None):
    # connect to VISOR backend service
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect((extra_prms['backend_host'], extra_prms['backend_port']))
    except error, msg:
        print 'Connect failed', msg
        raise error

    sock.settimeout(TCP_TIMEOUT)

    # construct VISOR backend function call
    func_in = dict(func=extra_prms['func'],
                   query_id=extra_prms['query_id'],
                   impath=out_dict['clean_fn'],
                   from_dataset=0)
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
        try:
            context = zmq.Context()

            impath_sender = context.socket(zmq.REQ)
            impath_sender.connect(extra_prms['zmq_impath_return_ch'])
            impath_sender.send(str(out_dict['clean_fn']))
            impath_sender.recv()

        finally:
            impath_sender.close()
            context.term()
