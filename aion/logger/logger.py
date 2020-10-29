# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import asyncio
from time import time
from logging import basicConfig, getLogger, DEBUG

component_name = "None"
logger = None


def initialize_logger(component, level=DEBUG):
    global component_name
    global logger
    component_name = component
    basicConfig(
        format='%(asctime)s000 - %(levelname)-4s - %(process)-5d - %(name)s - %(message)s',
        level=level,
    )
    logger = getLogger(component_name)


def lprint(*args):
    global logger
    message = ", ".join([str(x) for x in args])
    logger.debug(message)


def lprint_exception(e):
    logger.exception(f'{e}')


def function_log(func):
    if asyncio.iscoroutinefunction(func):
        async def async_wrapper(*args, **kwargs):
            func_name = func.__name__
            st = time()
            # start log
            lprint("Start: " + func_name)
            res = await func(*args, **kwargs)
            # finish log
            lprint("Finish:" + func_name + "(time:{})".format(time() - st))
            return res

        return async_wrapper
    else:
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            st = time()
            # start log
            lprint("Start: " + func_name)
            res = func(*args, **kwargs)
            # finish log
            lprint("Finish:" + func_name + "(time:{})".format(time() - st))
            return res

        return wrapper
