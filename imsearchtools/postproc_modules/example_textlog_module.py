#!/usr/bin/env python

import json

def callback_func(out_dict, extra_prms=None):
    with open('test.txt','a') as myfile:
        myfile.write('\n')
        myfile.write('OUT_DICT:\n')
        myfile.write(json.dumps(out_dict))
        if extra_prms:
            myfile.write('\nEXTRA_PRMS:\n')
            myfile.write(json.dumps(extra_prms))
        myfile.write('\n')
