#!/usr/bin/env python3
# encoding: utf-8

from gpiozero import MotionSensor
from signal import pause


def it_is_on():
    print("It is on!")


def it_is_off():
    print("It's out!")


sensor = MotionSensor(4)

sensor.when_motion = it_is_on
sensor.when_no_motion = it_is_off

pause()
