#!/usr/bin/env python3
# encoding: utf-8

import asyncio
import os
from shlex import quote

from aiohttp import web

_current_dir = os.path.realpath(os.path.dirname(__file__))
MEDIA_DIR = os.path.join(_current_dir, 'media')


def setup():
    # make sure media dir exists
    os.makedirs(MEDIA_DIR, 0o770, exist_ok=True)


async def run_command(cmd, kwargs):
    # TODO: pass args to command line
    args_str = ""
    cmd = cmd.format(quote(args_str))

    proc = await asyncio.create_subprocess_exec(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    await proc.wait()

    return proc


async def take_some_pictures(request):
    """
    Receives an image and writes it down to disk.
    """
    # prepare args to start pictures
    kwargs = {
        'camera_mode': None,
        'count': 1,
        'format': 'jpeg',
        'media_dir': MEDIA_DIR,
        'save': True,
        'send': True,
        'sleep': 0,
        'upload_url': os.environ['KOTOMERA_PICTURE_URL']
    }
    # use async to start "take_a_picture" script
    task = asyncio.ensure_future(
        run_command("python3 take_a_picture.py {}", kwargs)
    )
    # check if script didn't fail in first second
    await asyncio.sleep(1)
    # return response
    if task.done():
        result = task.result()
        if result.returncode == 0:
            return web.Response(text='Done')
        else:
            msg = "Fial\n" + result.stderr.read()
            return web.Response(text=msg)
    return web.Response(text='Working')


if __name__ == "__main__":
    setup()
    app = web.Application()
    app.router.add_routes([
        web.post('/take_a_picture', take_some_pictures),
        web.get('/take_a_picture', take_some_pictures),  # for dev use only
    ])

    web.run_app(app, port=8075)
