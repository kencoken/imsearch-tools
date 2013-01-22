#!/usr/bin/env python

from socket import *
from flask import json

TCP_TERMINATOR = "$$$"
SUCCESS_FIELD = "success"
TCP_TIMEOUT = 86400.00

def callback_func(out_dict, extra_prms=None):
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect((extra_prms['backend_host'], extra_prms['backend_port']))
    except error, msg:
        print 'Connect failed', msg

    sock.settimeout(TCP_TIMEOUT)

    func_in = dict(func=extra_prms['func'],
                   query_id=extra_prms['query_id'],
                   impath=out_dict['clean_fn'],
                   from_dataset=0)
    request = json.dumps(func_in) + TCP_TERMINATOR

    sock.send(request)

    response = ""
    while 1:
        try:
            data = sock.recv(1024)
            if not data:
                break
            response += data
        except socket.timeout:
            print 'Socket timeout'
            sock.close()
            
    sock.close()
