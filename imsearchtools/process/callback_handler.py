#!/usr/bin/env python

"""
Module: callback_handler
Author: Ken Chatfield <ken@robots.ox.ac.uk>
Created on: 29 Jan 2013
"""

import logging
import gevent
import time
from multiprocessing import cpu_count

log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)

class CallbackHandler(object):
    """Class for wrapping callbacks

    Initializer Args:
        worker_func: the callback to run when calling `run_callback()`
        task_count: the number of times `run_callback()` will be called
        [worker_count]: the number of workers to use (default: # CPUs)


    On launch a pool of `worker_count` workers is started, which will then
    process any tasks added to the task queue by calling `run_callback()`
    (the parameters of the callback function can be passed directly as
    parameters to `run_callback()`).

    Once `task_count` tasks have been run and completed, the workers will
    shut down. Wait for this condition by calling `join()`.
    """
    def __init__(self, worker_func, task_count, worker_count=-1):
        # initialize completion task worker pool
        # if number of workers is not specified, set it to the number of CPUs
        if worker_count == -1:
            worker_count = cpu_count()
        self.worker_pool = gevent.pool.Pool(size=worker_count)
        self.worker_pool_closed = False
        # store requested task count and callback function
        self.task_count = task_count
        self.worker_func = worker_func

    def run_callback(self, *args, **kwargs):
        #log.debug('Starting task for file: %s', out_dict['clean_fn'])
        if not self.worker_pool_closed:
            log.debug('Starting task')
            worker_params = dict(args=args,
                                 kwargs=kwargs)
            # spawn worker through greenlet, so function does not block when pool is full
            spawn_func = lambda self, worker_params: self.worker_pool.spawn(self._callback_func, worker_params)
            gevent.spawn(spawn_func, self, worker_params)
        

    def skip(self):
        log.debug('Skipping task')
        self._dec_task_count_skipped()

    def join(self):
        # waiting for all tasks to complete
        log.debug('Waiting all tasks to be completed...')
        while self.task_count > 0:
            time.sleep(0.05)
        self.worker_pool_closed = True
        self.worker_pool.join()
        log.debug('All tasks completed!')

    def terminate(self):
        log.debug('Terminating workers early...')
        self.worker_pool_closed = True
        self.worker_pool.kill()
        self.worker_pool.join()
        log.debug('Done terminating!')

    def _callback_func(self, worker_params):
        self.worker_func(*worker_params['args'], **worker_params['kwargs'])
        self._dec_task_count_completed()
        
    def _dec_task_count_completed(self):
        self.task_count = self.task_count - 1
        log.debug('Completed post-computation, remaining tasks: %d', self.task_count)

    def _dec_task_count_skipped(self):
        self.task_count = self.task_count - 1
        log.debug('Skipped post-computation, remaining tasks: %d', self.task_count)

    
