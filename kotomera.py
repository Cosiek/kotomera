#!/usr/bin/env python3
# encoding: utf-8

import asyncio
import os
from os.path import dirname, join, realpath

from aiohttp import web
from gpiozero import MotionSensor

from helpers import async_to_sync
from manager import CameraManager
import picture_processors as pic_proc

_current_dir = realpath(dirname(__file__))
MEDIA_DIR = join(_current_dir, 'media')


def setup():
    # make sure media dir exists
    os.makedirs(MEDIA_DIR, 0o770, exist_ok=True)

# VIEWS #######################################################################

async def take_a_picture(request):
    will = await request.app['cam_manager'].take_a_picture()
    return web.Response(text=str(will))

# APPLICATION #################################################################

if __name__ == "__main__":
    # prepare dirs
    setup()
    # get loop
    loop = asyncio.new_event_loop()
    # prepare web server
    app = web.Application()
    app.router.add_routes([
        web.post('/picture', take_a_picture),
    ])
    # prepare camera manager
    app['cam_manager'] = CameraManager()
    app['cam_manager'].add_picture_processor(
        pic_proc.SaveToDiskPictureProcessor())
    app['cam_manager'].add_picture_processor(
        pic_proc.SendToKotomeraPictureProcessor())
    # prepare motion detector
    sensor = MotionSensor(4)
    sensor.when_motion = async_to_sync(app['cam_manager'].when_motion)
    sensor.when_no_motion = async_to_sync(app['cam_manager'].when_no_motion)

    web.run_app(app, port=8075, loop=loop)

