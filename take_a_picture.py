#!/usr/bin/env python3
# encoding: utf-8

from datetime import datetime
from io import BytesIO
import os
from os.path import join, realpath, dirname
from time import sleep

import requests

from camera import get_camera

_current_dir = realpath(dirname(__file__))


def take_a_series_of_pictures(cam, count: int = 0, **kwargs) -> bytes:
    """
    Takes a series of 'count' pictures, and yields them as they are ready.
    """
    for i in range(count):
        yield take_a_picture(cam, kwargs['format'])


def take_a_picture(cam, format_: str) -> bytes:
    """
    Captures a picture from a camera and returns its bytes "value".
    """
    content = BytesIO()
    try:
        cam.capture(content, format=format_)
        return content.getvalue()
    finally:
        content.close()


def save_to_disk(pic: bytes, **kwargs):
    """
    Saves given picture data to disk.

    The target file path is generated form combination of 'media_dir' and a
    filename generated from current date and time.
    """
    # get file name
    filename = str(datetime.now()).replace(" ", "_") + kwargs['format']
    file_path = join(kwargs['media_dir'], filename)
    # write it to a file
    with open(file_path, 'wb') as f:
        f.write(pic)


def send_to_server(pic: bytes, **kwargs):
    """
    Uploads a picture to a server given by 'upload_url'
    """
    requests.post(
        kwargs['upload_url'],
        data=pic,
        headers={'Content-Type': 'application/' + kwargs['format']}
    )


def process_picture(pic: bytes, **kwargs):
    """
    Calls required picture processors.
    """
    for name, processor in [('save', save_to_disk), ('send', send_to_server)]:
        if kwargs.get(name, False):
            processor(pic, **kwargs)


if __name__ == "__main__":
    # TODO: parse args
    kwargs = {
        'camera_mode': None,
        'count': 1,
        'format': 'jpeg',
        'media_dir': join(_current_dir, 'media'),
        'save': True,
        'send': True,
        'sleep': 0,
        'upload_url': os.environ['KOTOMERA_PICTURE_URL']
    }
    # prepare a camera
    cam = get_camera(**kwargs)
    # take a series of pictures
    for pic in take_a_series_of_pictures(cam, **kwargs):
        # process this picture
        process_picture(pic)
        # sleep if required
        if kwargs['sleep']:
            sleep(kwargs['sleep'])
    # cleanup
    cam.close()
