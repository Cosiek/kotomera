#!/usr/bin/env python3
# encoding: utf-8

from datetime import datetime
import os
from os.path import join, realpath, dirname

from camera import get_camera

_current_dir = realpath(dirname(__file__))


class DummyFileLike:

    def __init__(self, config):
        self.sub_files = []
        self.set_sub_files(config)

    def write(self, data):
        for sf in self.sub_files:
            sf.write(data)

    def set_sub_files(self, config):
        if config['save']:
            file_name = f"{datetime.now().timestamp()}.{config['format']}"
            self.sub_files.append(
                open(join(config['media_dir'], file_name), 'wb'))

        if config['send']:
            pass

    def close(self):
        for sf in self.sub_files:
            sf.close()


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
    dummy_file = DummyFileLike(kwargs)
    try:
        # prepare a camera
        cam = get_camera(**kwargs)
        cam.start_recording(dummy_file, format=kwargs['format'])
    finally:
        # cleanup
        cam.stop_recording()
        cam.close()
        dummy_file.close()
