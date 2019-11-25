#!/usr/bin/env python3
# encoding: utf-8

from picamera import PiCamera


def get_camera_options(**kwargs):
    default = {
        'resolution': (640, 480),
        'framerate': 1,
        'sensor_mode': 3,
    }

    for key, val in kwargs.items():
        if key in default:
            default[key] = val

    return default


def adjust_camera(camera, **kwargs):
    modes = {
        'night': set_to_night_vision,
    }
    if kwargs['camera_mode']:
        # TODO: don't overwrite options from kwargs
        modes[kwargs['camera_mode']](camera)


def get_camera(**kwargs):
    """
    Returns a PiCamera object, adjusted with given options.

    Remember to close the camera once you're done with it.
    """
    opts = get_camera_options()
    camera = PiCamera(**opts)
    adjust_camera(camera, **kwargs)

# CAMERA MODES ================================================================

def set_to_night_vision(cam):
    cam.brightness = 75
    cam.exposure_mode = 'night'
    cam.framerate = 1  # set framerate to 1fps
    cam.iso = 1600
    cam.sensor_mode = 3  # force long exposure mode
    cam.shutter_speed = 1000000  # set shutter speed to 1s

    # TODO?: cam.flash_mode = 'on'
    # TODO?: IR diodes
