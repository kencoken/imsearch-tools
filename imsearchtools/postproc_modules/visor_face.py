#!/usr/bin/env python

import Pyro4
from gevent_zeromq import zmq



def callback_func(out_dict, extra_prms=None):
    # connect to VISOR backend service
    #sock = socket(AF_INET, SOCK_STREAM)
    #try:
    #    sock.connect((extra_prms['backend_host'], extra_prms['backend_port']))
    #except error, msg:
    #    print 'Connect failed', msg
    #    raise error
    backed_server = Pyro4.Proxy("PYRONAME:face_retrieval_backend_v0")
    #backed_server._pyroOneway.add("add_pos_trs")
    backed_server.add_pos_trs(extra_prms['query_id'], out_dict['orig_fn'])
                                         
    
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
