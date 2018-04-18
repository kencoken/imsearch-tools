#!/usr/bin/env python

import os
import socket
import random
import logging
log = logging.getLogger(__name__)

from gevent_zeromq import zmq
from flask import json

TCP_TERMINATOR = "$$$"
SUCCESS_FIELD = "success"
TCP_TIMEOUT = 86400.00

def callback_func(out_dict, extra_prms=None):
    # connect to VISOR backend service
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    debug_cb_id = random.getrandbits(128)
    debug_cb_id = '%032x' % debug_cb_id

    log.debug('VISOR CATEGORY: Connecting to backend (%s)...', debug_cb_id)
    sock.connect((extra_prms['backend_host'], extra_prms['backend_port']))
    log.debug('VISOR CATEGORY: Connected to backend (%s)', debug_cb_id)

    sock.settimeout(TCP_TIMEOUT)

    # generate feature file path from image file path
    imfn = os.path.basename(out_dict['clean_fn'])
    (featfn, imext) = os.path.splitext(imfn)
    featfn += '.bin'
    featpath = os.path.join(extra_prms['featdir'], featfn)
    extra_params = dict()
    if 'detector' in extra_prms:
        extra_params['detector'] = extra_prms['detector']
    # construct VISOR backend function call
    func_in = dict(func=extra_prms['func'],
                   query_id=extra_prms['query_id'],
                   impath=out_dict['clean_fn'],
                   featpath=featpath,
                   from_dataset=0,
                   extra_params=extra_params)
    request = json.dumps(func_in)

    log.info('VISOR CATEGORY: Prepared request to VISOR backend (%s): %s', debug_cb_id, request)

    request = request + TCP_TERMINATOR

    # send request to VISOR backend
    total_sent = 0
    while total_sent < len(request):
        log.debug('VISOR CATEGORY: Sending request chunk (%s)...', debug_cb_id)
        sent = sock.send(request[total_sent:])
        if sent == 0:
            raise RuntimeError("VISOR CATEGORY: Socket connection broken")
        total_sent = total_sent + sent

    log.info('VISOR CATEGORY: Request sent (%s)', debug_cb_id)

    # receive response from VISOR backend
    response = ""
    term_idx = -1
    while term_idx < 0:
        try:
            log.debug('VISOR CATEGORY: Receiving response chunk (%s)...', debug_cb_id)
            rep_chunk = sock.recv(1024)
            if not rep_chunk:
                log.error('VISOR CATEGORY: Connection closed! (%s)', debug_cb_id)
                sock.close()
                log.debug('VISOR CATEGORY: Closed socket')
                break
            response = response + rep_chunk
            term_idx = response.find(TCP_TERMINATOR)
        except socket.timeout:
            log.error('VISOR CATEGORY: Socket timeout! (%s)', debug_cb_id)
            sock.close()
            log.debug('VISOR CATEGORY: Closed socket (%s)', debug_cb_id)
            break

    log.debug('VISOR CATEGORY: Received response (%s): %s', debug_cb_id, response)
    sock.close()
    log.debug('VISOR CATEGORY: Closed socket (%s)', debug_cb_id)

    # return URL on ZMQ channel if specified in extra_prms
    if 'zmq_impath_return_ch' in extra_prms:
        log.info('VISOR CATEGORY: Returning image URL on ZMQ channel: %s', extra_prms['zmq_impath_return_ch'])
        created_sock = True
        try:
            # either reuse or create new zmq socket
            if 'zmq_impath_return_sock' not in extra_prms:
                # either reuse or create new zmq context
                # (to create socket)
                if 'zmq_context' in extra_prms:
                    log.info('VISOR CATEGORY: Reusing ZMQ_CONTEXT')
                    context = extra_prms['zmq_context']
                else:
                    log.info('VISOR CATEGORY: Generating new ZMQ_CONTEXT')
                    context = zmq.Context()

                impath_sender = context.socket(zmq.REQ)
                impath_sender.connect(extra_prms['zmq_impath_return_ch'])
            else:
                created_sock = False
                log.info('VISOR CATEGORY: Reusing ZMQ_SOCKET')
                impath_sender = extra_prms['zmq_impath_return_sock']

            impath_sender.send(str(out_dict['clean_fn']))
            impath_sender.recv()
            log.info('VISOR CATEGORY: Completed request')

        finally:
            if created_sock: impath_sender.close()
    else:
        log.info('VISOR CATEGORY: Not returning image URL over ZMQ channel (not specified)')
