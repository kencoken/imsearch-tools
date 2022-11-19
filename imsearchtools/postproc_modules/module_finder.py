#!/usr/bin/env python

import os
import importlib

def get_module_callback(module_name):
    try:
        module = importlib.import_module('.'+module_name, 'imsearchtools.postproc_modules')
        callback_func = module.callback_func
    except ImportError as err:
        avail_modules = get_module_list()
        raise ImportError("Could not find postproc module with name: '%s' (available modules are %s): %s" % (module_name, avail_modules, str(err)))
    except AttributeError:
        raise AttributeError("Postproc module with name '%s' did not contain required 'callback_func(out_dict)' function" % module_name)

    return callback_func

def get_module_list():
    # return a list of all py files in current directory which aren't this file
    # these are assumed to be the supported modules
    modnames = [os.path.splitext(modname)[0]
                for modname in os.listdir(os.path.dirname(os.path.realpath(__file__)))
                if modname.endswith(('.py','.pyc','.pyo'))
                and os.path.splitext(modname)[0] != os.path.splitext(os.path.basename(__file__))[0]
                and os.path.splitext(modname)[0] != '__init__']
    return list(set(modnames))
