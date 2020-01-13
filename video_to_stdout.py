#!/usr/bin/env python3
# encoding: utf-8

import os
from os.path import join, realpath, dirname

from camera import get_camera

_current_dir = realpath(dirname(__file__))


class Dummy():

    def __init__(self):
        pass

    def write(self, data):
        print(type(data), len(data))

    def flush(self):
        print("flush")


if __name__ == "__main__":
    # TODO: parse args
    kwargs = {
        'camera_mode': None,
        'format': 'h264',
        'media_dir': join(_current_dir, 'media'),
        'save': True,
        'send': True,
        'upload_url': os.environ['KOTOMERA_VIDEO_URL']
    }
    # prepare a writer
    dummy_file = Dummy()
    cam = get_camera(**kwargs)
    cam.start_recording(dummy_file, format=kwargs['format'])
    cam.wait_recording(60)
    cam.stop_recording()
    cam.close()
