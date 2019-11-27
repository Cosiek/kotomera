#!/usr/bin/env python3
# encoding: utf-8

from datetime import datetime
from io import BytesIO
import os
from os.path import join, realpath, dirname

import requests

from camera import get_camera

_current_dir = realpath(dirname(__file__))


class DummyFileLike:

    def __init__(self, config):
        self.sub_files = []
        self.config = config

        self.set_sub_files()

    def write(self, data):
        for sf in self.sub_files:
            sf.write(data)

    def set_sub_files(self):
        if self.config['save']:
            self.sub_files.append(self.get_system_file())

        if self.config['send']:
            self.sub_files.append(self.get_network_file())

    def close(self):
        for sf in self.sub_files:
            sf.close()

    def get_system_file(self):
        file_name = f"{datetime.now().timestamp()}.{self.config['format']}"
        return open(join(self.config['media_dir'], file_name), 'wb')

    def get_network_file(self):
        # prepare a file like object
        nf = BytesIO()
        # set it as a request data source
        requests.post(self.config['upload_url'], data=nf)
        # return it
        return nf


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
