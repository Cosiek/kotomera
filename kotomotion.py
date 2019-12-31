#!/usr/bin/env python3
# encoding: utf-8

from gpiozero import MotionSensor
import requests
from signal import pause

import urls


def callback():
    requests.get(urls.get_kotomera_url('take_a_picture'))


pir = MotionSensor(4)
pir.when_motion = callback

pause()
