#!/usr/bin/env python3
# encoding: utf-8

import asyncio
from datetime import datetime

import os

import aiohttp
from aiohttp import web
import aiohttp_jinja2
import jinja2

import urls

_current_dir = os.path.realpath(os.path.dirname(__file__))
STATICS_DIR = os.path.join(_current_dir, 'statics')
MEDIA_DIR = os.path.join(_current_dir, 'media')
PICTURES_DIR = os.path.join(MEDIA_DIR, 'pictures')
VIDEOS_DIR = os.path.join(MEDIA_DIR, 'videos')


def setup(app):
    # make sure media dirs exists
    os.makedirs(STATICS_DIR, 0o770, exist_ok=True)
    os.makedirs(MEDIA_DIR, 0o770, exist_ok=True)
    os.makedirs(PICTURES_DIR, 0o770, exist_ok=True)
    os.makedirs(VIDEOS_DIR, 0o770, exist_ok=True)

    # init templates
    templates_path = os.path.join(_current_dir, 'templates')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(templates_path))


async def main(request):
    ctx = {'timestamp': datetime.now().timestamp()}
    return aiohttp_jinja2.render_template("main.html", request, ctx)

# =============================================================================
# CONTROLS ====================================================================
# =============================================================================


async def handle_request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                return web.json_response(await resp.json())
        except aiohttp.ClientConnectorError:
            return web.json_response({
                'request_accepted': False,
                'state': None,
                'msg': 'Failed to connect to kotomera (ClientConnectorError)'
            })


async def take_a_picture(request):
    url = urls.get_kotomera_url('take_a_picture')
    return await handle_request(url)


async def start_recording(request):
    url = urls.get_kotomera_url('start_recording')
    return await handle_request(url)


async def stop_recording(request):
    url = urls.get_kotomera_url('stop_recording')
    return await handle_request(url)


async def start_motion_detection(request):
    url = urls.get_kotomera_url('start_motion_detection')
    return await handle_request(url)


async def stop_motion_detection(request):
    url = urls.get_kotomera_url('stop_motion_detection')
    return await handle_request(url)


async def start_interval(request):
    url = urls.get_kotomera_url('start_interval')
    return await handle_request(url)


async def stop_interval(request):
    url = urls.get_kotomera_url('stop_interval')
    return await handle_request(url)


# =============================================================================
# RECEIVERS ===================================================================
# =============================================================================


async def picture_upload(request):
    """
    Receives an image and writes it down to disk.
    """
    filename = str(datetime.now()).replace(" ", "_") + '.jpg'
    print("Writing ", filename)
    with open(os.path.join(PICTURES_DIR, filename), 'wb') as f:
        async for data, end in request.content.iter_chunks():
            f.write(data)

    return web.Response(text='Ok')


async def video_stream_upload(request):
    """
    Receives a video stream and writes it to a file.
    """
    filename = str(datetime.now()).replace(" ", "_") + '.h264'
    print("Writing ", filename)
    with open(os.path.join(VIDEOS_DIR, filename), 'wb') as f:
        async for data, end in request.content.iter_chunks():
            f.write(data)

    return web.Response(text='Ok')


# =============================================================================
# RESOURCES ===================================================================
# =============================================================================


async def pictures(request):
    pictures = []
    prefix = urls.KOTOSERVER['media_url'] + '/' + PICTURES_DIR.lstrip(MEDIA_DIR)
    for file_ in os.listdir(PICTURES_DIR):
        pictures.append('/'.join((prefix, file_)))

    return web.json_response(pictures)


async def video_stream_download(request):
    """
    Responses with live video stream
    """
    response = web.StreamResponse(headers={'Content-Type': 'video/mp4'})

    await response.prepare(request)

    with open("/home/cosiek/Projekty/kotomera/media/Rooster.mp4", "rb") as f:
        for line in f.readlines():
            await response.write(line)

    await response.write_eof()
    return response


if __name__ == "__main__":
    app = web.Application()

    setup(app)

    app.add_routes([web.static(urls.KOTOSERVER['static_url'], STATICS_DIR, show_index=True)])
    app.add_routes([web.static(urls.KOTOSERVER['media_url'], MEDIA_DIR, show_index=True)])

    app.router.add_routes([
        web.get('/', main),
        # controls
        web.get('/take_a_picture', take_a_picture),
        web.get('/start_recording', start_recording),
        web.get('/stop_recording', stop_recording),
        web.get('/start_motion_detection', start_motion_detection),
        web.get('/stop_motion_detection', stop_motion_detection),
        web.get('/start_interval', start_interval),
        web.get('/stop_interval', stop_interval),
        # receivers
        web.post(urls.KOTOSERVER['picture_upload'], picture_upload),
        web.post(urls.KOTOSERVER['video_upload'], video_stream_upload),
        # resources
        web.get('/pictures', pictures),
        web.get('/video_stream', video_stream_download),
    ])

    web.run_app(app, port=urls.KOTOSERVER['port'])
