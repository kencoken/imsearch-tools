#!/usr/bin/env python

import zmq.green as zmq


def callback_func(out_dict, extra_prms=None):

    # send back the file name
    print "\n\n", out_dict['clean_fn'], "\n\n";

    # return URL on ZMQ channel
    if not('zmq_impath_return_ch' in extra_prms):

        print "rr_text_query::callback_func: error, need zmq_impath_return_ch in extra_prms";

    else:
        try:
            context = zmq.Context()

            impath_sender = context.socket(zmq.REQ)
            impath_sender.connect(extra_prms['zmq_impath_return_ch'])
            impath_sender.send(str(out_dict['clean_fn']))
            impath_sender.recv()

        finally:
            impath_sender.close()
            context.term()
