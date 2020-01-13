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

        #if self.config['send']:
        #    self.sub_files.append(self.get_network_file())

    def close(self):
        for sf in self.sub_files:
            sf.close()

    def get_system_file(self):
        file_name = f"{datetime.now().timestamp()}.{self.config['format']}"
        return open(join(self.config['media_dir'], file_name), 'wb')

    def get_network_file(self):
        class Dummy:
            def __init__(self, config):
                self.nf = BytesIO()
                self.used = False
                self.config = config

            def write(self, data):
                self.nf.write(data)
                if not self.used:
                    self.used = True
                    requests.post(self.config['upload_url'], data=self.nf,
                                  stream=True)

            def __iter__(self):
                return self.read()

            def close(self):
                self.nf.close()
        # prepare a file like object
        #nf = BytesIO()
        # set it as a request data source
        #requests.post(self.config['upload_url'], data=nf)
        # return it
        return Dummy(self.config)

    def get_network_fileX(self):
        import socket

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(self.config['server_ip'], self.config['server_port'])

        return client_socket.makefile('wb')

    def get_network_file(self):

        # prepare data writer class
        class NetworkFileWrapper:

            def __init__(self, parent):
                self.parent = parent

                import socket

                self.rsock, self.wsock = socket.socketpair()
                async def iter():
                    while True:
                        yield await self.rsock.read()

                import asyncio
                import aiohttp
                with aiohttp.ClientSession() as session:
                    asyncio.ensure_future(
                        session.post(parent.config['upload_url'], data=iter()))

            def write(self, data):
                self.wsock.write(data)

        return NetworkFileWrapper(self)


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
        file_name = f"{datetime.now().timestamp()}.{kwargs['format']}"

        cam = get_camera(**kwargs)
        with open(join(kwargs['media_dir'], file_name), 'wb') as dummy_file:
            cam.start_recording(dummy_file, format=kwargs['format'])
        #while True:
        #    cam.wait_recording(60)
    finally:
        # cleanup
        #cam.stop_recording()
        cam.close()
        #dummy_file.close()
