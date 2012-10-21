#!/usr/bin/env python

"""
Module: callback_handler
Author: Ken Chatfield <ken@robots.ox.ac.uk>
        Kevin McGuinness <kevin.mcguinness@eeng.dcu.ie>
Created on: 20 Oct 2012
"""

import logging
import zmq

from multiprocessing import Process
from multiprocessing import cpu_count

log = logging.getLogger(__name__)

ZMQ_TASK_LAUNCH_CH = 'ipc:///tmp/zmq_imsearchtools_task_ch'#'tcp://127.0.0.1:5557'
ZMQ_TASK_COUNT_DEC_CH = 'ipc:///tmp/zmq_imsearchtools_tcdec_ch'#'tcp://127.0.0.1:5558'
ZMQ_TASK_RESULT_CH = 'ipc:///tmp/zmq_imsearchtools_result_ch'#'tcp://127.0.0.1:5559'
ZMQ_WORKER_CONTROL_CH = 'ipc:///tmp/zmq_imsearchtools_control_ch'#'tcp://127.0.0.1:5560'

ZMQ_RESULT_SKIPPING = 'SKIPPING'
ZMQ_RESULT_DONE = 'DONE'
ZMQ_CONTROL_DONE = 'FINISHED'

class CallbackHandler(object):
    """Class for wrapping callbacks using ZMQ

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
        # initialize completion task workers
        self.workers = CallbackTaskWorkers(worker_func, worker_count)

        # start result manager
        self.result_manager = Process(target=result_manager,
                                      args=(task_count,))
        self.result_manager.start()

        # initialize completion task runner
        self.runner = CallbackTaskRunner()

    def run_callback(self, *args, **kwargs):
        self.runner.run(*args, **kwargs)

    def skip(self):
        self.runner.skip()

    def join(self):
        # wait first for the result manager to terminate
        self.result_manager.join()
        # this should cause the workers to also terminate,
        #  but wait for them to explicitly say they're done too
        self.workers.join()

class CallbackTaskRunner(object):
    """Class used internally by CallbackHandler to launch tasks"""
    def __init__(self):
        context = zmq.Context()
        # channel -> worker
        self.task_sender = context.socket(zmq.PUSH)
        self.task_sender.bind(ZMQ_TASK_LAUNCH_CH)
        # channel -> result_manager
        self.tcdec_sender = context.socket(zmq.PUB)
        self.tcdec_sender.bind(ZMQ_TASK_COUNT_DEC_CH)

    def run(self, *args, **kwargs):
        #log.debug('Starting task for file: %s', out_dict['clean_fn'])
        log.debug('Starting task')
        params = dict(args=args,
                     kwargs=kwargs)
        self.task_sender.send_json(params)

    def skip(self):
        log.debug('Skipping task')
        self.tcdec_sender.send(ZMQ_RESULT_SKIPPING)

class CallbackTaskWorkers(object):
    """Class used internally by CallbackHandler to launch a pool of workers"""
    def __init__(self, worker_func, worker_count=-1):
        # if number of workers is not specified, set it to the number of CPUs
        if worker_count == -1:
            worker_count = cpu_count()
            
        self.workers = [None]*worker_count
        for wrk_num in range(worker_count):
            self.workers[wrk_num] = Process(target=self._callback_worker,
                                            args=(wrk_num, worker_func))
            self.workers[wrk_num].start()

    def join(self):
        for worker in self.workers:
            worker.join()

    def _callback_worker(self, wrk_num, worker_func):
        log.debug('Initializing worker number %d', wrk_num)

        context = zmq.Context()
        # channel <- run_completion_task
        task_receiver = context.socket(zmq.PULL)
        task_receiver.connect(ZMQ_TASK_LAUNCH_CH)
        # channel -> result_manager
        result_sender = context.socket(zmq.PUSH)
        result_sender.connect(ZMQ_TASK_RESULT_CH)
        # channel <- result_manager (CONTROL)
        control_receiver = context.socket(zmq.SUB)
        control_receiver.connect(ZMQ_WORKER_CONTROL_CH)
        control_receiver.setsockopt(zmq.SUBSCRIBE, "")

        poller = zmq.Poller()
        poller.register(task_receiver, zmq.POLLIN)
        poller.register(control_receiver, zmq.POLLIN)

        # loop and accept messages from both task and control channels
        while True:
            socks = dict(poller.poll())

            # handle callback launch requests
            if socks.get(task_receiver) == zmq.POLLIN:
                worker_params = task_receiver.recv_json()
                #log.debug('Launching post-computation for file: %s',
                #         out_dict['clean_fn'])
                worker_func(*worker_params['args'], **worker_params['kwargs'])
                result_sender.send(ZMQ_RESULT_DONE)

            # handle control commands from manager
            if socks.get(control_receiver) == zmq.POLLIN:
                control_message = control_receiver.recv()
                if control_message == ZMQ_CONTROL_DONE:
                    log.debug('Terminating worker number %d', wrk_num)
                    break

    

def result_manager(num_tasks):
    """Function used internally by CallbackHandler to collect results of tasks"""

    context = zmq.Context()

    # channel <- completion_worker
    result_receiver = context.socket(zmq.PULL)
    result_receiver.bind(ZMQ_TASK_RESULT_CH)
    # channel -> completion_worker (CONTROL)
    control_sender = context.socket(zmq.PUB)
    control_sender.bind(ZMQ_WORKER_CONTROL_CH)
    # channel <- skip_completion_task
    tcdec_receiver = context.socket(zmq.SUB)
    tcdec_receiver.connect(ZMQ_TASK_COUNT_DEC_CH)
    tcdec_receiver.setsockopt(zmq.SUBSCRIBE, "")

    poller = zmq.Poller()
    poller.register(result_receiver, zmq.POLLIN)
    poller.register(tcdec_receiver, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())

        # handle results from workers
        if socks.get(result_receiver) == zmq.POLLIN:
            result_message = result_receiver.recv()
            if result_message == ZMQ_RESULT_DONE:
                num_tasks -= 1
                log.debug('Completed post-computation, remaining tasks: %d', num_tasks)

        # handle counter decrementing
        if socks.get(tcdec_receiver) == zmq.POLLIN:
            result_message = tcdec_receiver.recv()
            if result_message == ZMQ_RESULT_SKIPPING:
                num_tasks -= 1
                log.debug('Skipped post-computation, remaining tasks: %d', num_tasks)

        # break from loop when all tasks completed
        if num_tasks == 0:
            log.debug('All tasks done - terminating workers')
            break

    # terminate all workers when all tasks completed
    control_sender.send(ZMQ_CONTROL_DONE)
    
