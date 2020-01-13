#!/usr/bin/env python3
# encoding: utf-8

import os

KOTOSERVER = {
    'host': os.environ.get('KOTOSERVER_HOST'),
    'port': 8075,
    'static_url': '/statics',
    'media_url': '/media',
    # upload urls
    'picture_upload': '/picture_upload',
    'video_upload': '/video_stream_upload',
}

KOTOMERA = {
    'host': 'raspberrypi.local',
    'port': 8075,
    # control urls
    'take_a_picture': '/take_a_picture',
    'start_recording': '/start_recording',
    'stop_recording': '/stop_recording',
}


def get_kotoserver_url(target):
    return f"http://{KOTOSERVER['host']}:{KOTOSERVER['port']}{KOTOSERVER[target]}"


def get_kotomera_url(target):
    return f"http://{KOTOMERA['host']}:{KOTOMERA['port']}{KOTOMERA[target]}"
