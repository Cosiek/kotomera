#!/usr/bin/env python3
# encoding: utf-8

from datetime import datetime
from signal import pause

from gpiozero import MotionSensor
from picamera import PiCamera


CAMERA = PiCamera()
CAMERA.resolution = (1024, 768)


def it_is_on():
    print("It is on!")
    name = str(datetime.now()).replace(" ", "_")
    CAMERA.capture(f'{name}.jpg')


def it_is_off():
    print("It's out!")


sensor = MotionSensor(4)

sensor.when_motion = it_is_on
sensor.when_no_motion = it_is_off

pause()
