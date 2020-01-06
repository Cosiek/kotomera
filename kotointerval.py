#!/usr/bin/env python3
# encoding: utf-8

from time import sleep
import requests

import urls


def callback():
    try:
        requests.get(urls.get_kotomera_url('take_a_picture'))
    except requests.ConnectionError:
        pass


while True:
    callback()
    sleep(15)
