#!/usr/bin/env python3
# encoding: utf-8

import asyncio
from io import BytesIO
import os
from signal import pause

import aiohttp
from gpiozero import MotionSensor
from picamera import PiCamera

from cam_handling import get_camera_options, set_to_night_vision

CAMERA = PiCamera(**get_camera_options())
#set_to_night_vision(CAMERA)

URL = os.environ['KOTOMERA_URL']


def it_is_on():
    print("It is on!")
    # get image data
    file_content = BytesIO()
    CAMERA.capture(file_content, format='jpeg')
    # send image
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_jpg_file(file_content.getvalue()))
    file_content.close()


def it_is_off():
    print("It's out!")


async def send_jpg_file(file_content):
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('file', file_content, filename='whatever.jpg',
                       content_type='image/jpeg')

        async with session.post(URL, data=data) as resp:
            print(resp.status)
            print(await resp.text())


sensor = MotionSensor(4)

sensor.when_motion = it_is_on
sensor.when_no_motion = it_is_off

pause()
