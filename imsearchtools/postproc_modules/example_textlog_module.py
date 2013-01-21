#!/usr/bin/env python

import json

def callback_func(out_dict):
    with open('test.txt','a') as myfile:
        myfile.write(json.dumps(out_dict))
