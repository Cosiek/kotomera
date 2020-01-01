#!/usr/bin/env python3
# encoding: utf-8

import asyncio
import os
from shlex import quote

import aiohttp
from aiohttp import web

import urls

_current_dir = os.path.realpath(os.path.dirname(__file__))
MEDIA_DIR = os.path.join(_current_dir, 'media')


def setup():
    # make sure media dir exists
    os.makedirs(MEDIA_DIR, 0o770, exist_ok=True)


class CameraManager:

    # states
    IDLE = "idle"
    TAKING_A_PICTURE = "taking a picture"
    MAKING_A_VIDEO = "making a video"

    def __init__(self):
        self.state = self.IDLE
        self.process = None

        self.socket_pth = os.path.join(_current_dir, "socks")

    @property
    def is_busy(self):
        return self.state != self.IDLE

    @property
    def is_filming(self):
        return self.state == self.MAKING_A_VIDEO

    def _get_callback_function(self, url):

        async def callback(reader, writer):
            # prepare receiver async iterator
            async def receiver():
                while True:
                    data = await reader.readline()
                    if data:
                        yield data
                    else:
                        break
            # start sending data to target host
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=receiver()) as resp:
                    self.state = self.IDLE

        return callback

    async def take_a_picture(self):
        if self.is_busy:
            return
        self.state = self.TAKING_A_PICTURE

        url = urls.get_kotoserver_url('picture_upload')
        callback = self._get_callback_function(url)

        await asyncio.start_unix_server(callback, path=self.socket_pth)

        self.process = await asyncio.subprocess.create_subprocess_exec(
            "python3",
            "kotopicture.py",
            self.socket_pth,
        )

        await self.process.wait()

    async def start_recording(self):
        if self.is_busy:
            return
        self.state = self.MAKING_A_VIDEO

        url = urls.get_kotoserver_url('video_upload')
        callback = self._get_callback_function(url)

        await asyncio.start_unix_server(callback, path=self.socket_pth)

        self.process = await asyncio.subprocess.create_subprocess_exec(
            "python3",
            "kotovideo.py",
            self.socket_pth,
        )

        await self.process.wait()
        self.state = self.IDLE
        self.process = None

    async def stop_recording(self):
        if not self.is_filming:
            return False

        self.process.terminate()
        self.state = self.IDLE


class MotionDetectorManager:

    def __init__(self):
        self.process = None

    async def start(self):
        if self.process is not None:
            return "Already on"

        self.process = await asyncio.subprocess.create_subprocess_exec(
            "python3",
            "kotomotion.py"
        )
        await self.process.wait()
        self.process = None

    def stop(self):
        if self.process is None:
            return "Already off."

        self.process.terminate()
        self.process = None
        return "Terminated"


async def take_a_picture(request):
    resp = {
        'request_accepted': False,
        'state': request.app['cam'].state
    }
    if not request.app['cam'].is_busy:
        asyncio.ensure_future(request.app['cam'].take_a_picture())
        resp['request_accepted'] = True
    return web.json_response(resp)


async def start_recording(request):
    resp = {
        'request_accepted': False,
        'state': request.app['cam'].state
    }
    if not request.app['cam'].is_busy:
        asyncio.ensure_future(request.app['cam'].start_recording())
        resp['request_accepted'] = True
    return web.json_response(resp)


async def stop_recording(request):
    resp = {
        'request_accepted': False,
    }
    if request.app['cam'].is_filming:
        await request.app['cam'].stop_recording()
        resp['request_accepted'] = True
    resp['state'] = request.app['cam'].state
    return web.json_response(resp)


async def start_motion_detection(request):
    asyncio.ensure_future(request.app['motion'].start())
    return web.json_response({"msg": "OK?"})


async def stop_motion_detection(request):
    msg = request.app['motion'].stop()
    return web.json_response({"msg": msg})


if __name__ == "__main__":
    setup()
    app = web.Application()

    app['cam'] = CameraManager()
    app['motion'] = MotionDetectorManager()

    app.router.add_routes([
        web.get('/take_a_picture', take_a_picture),
        web.get('/start_recording', start_recording),
        web.get('/stop_recording', stop_recording),
        web.get('/start_motion_detection', start_motion_detection),
        web.get('/stop_motion_detection', stop_motion_detection),
    ])

    web.run_app(app, port=8075)
