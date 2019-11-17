#!/usr/bin/env python3
# encoding: utf-8

import asyncio


def async_to_sync(coro):
    """
    Returns a sync function that runs an async coroutine.

    :param coro: coroutine
    :return: sync function
    """
    def wrapper():
        print("is running?", coro)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(coro())

    return wrapper
