#!/usr/bin/env python
# encoding: utf-8

import asyncio
from datetime import datetime
import os
from os.path import dirname, join, realpath
import socket

from aiohttp import web


_current_dir = realpath(dirname(__file__))
MEDIA_DIR = join(_current_dir, 'media')


def setup():
    # make sure media dir exists
    os.makedirs(MEDIA_DIR, 0o770, exist_ok=True)


async def picture_upload(request):
    """
    Receives an image and writes it down to disk.
    """
    reader = await request.multipart()
    field = await reader.next()
    filename = str(datetime.now()).replace(" ", "_") + '.jpg'
    with open(os.path.join(MEDIA_DIR, filename), 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            f.write(chunk)

    return web.Response(text='Ok')


async def video_upload(request):
    """
    Receives a video stream and pipes it to VLC.
    """
    try:
        return web.Response("Start?")
    finally:
        await _video_upload()


async def _video_upload():
    """
    Receives a video stream and pipes it to VLC.
    """

    # Register the open socket to wait for data.
    sock = socket.socket()
    sock.bind(('0.0.0.0', 8888))
    sock.listen(0)
    conn, addr = sock.accept()

    #reader, writer = await asyncio.open_connection(sock=sock)

    # start VLC
    proc = await asyncio.create_subprocess_exec(
        'vlc', '--demux', 'h264', '-', stdin=asyncio.subprocess.PIPE)
    while True:
        # Repeatedly read 1k of data from the connection and write it to
        # the media player's stdin.
        data = await conn.read(1024)  # reader > conn
        print("Data?", bool(data))
        if not data:
            break
        proc.stdin.write(data)


if __name__ == "__main__":
    setup()
    app = web.Application()
    app.router.add_routes([
        web.post('/picture', picture_upload),
        web.get('/video', video_upload),
    ])

    web.run_app(app, port=8075)
