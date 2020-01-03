#!/usr/bin/env python3
# encoding: utf-8

from fractions import Fraction
import argparse
import socket

from picamera import PiCamera


def run(args):
    # establish socket connection
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(args.socket)
    connection = sock.makefile('wb')
    # get a camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    # implement night vision
    if args.night:
        camera.framerate = 1 # Fraction(1, 2)
        camera.shutter_speed = 100000  # set shutter speed to 1s
        camera.iso = 800
        camera.exposure_mode = 'night'
    # start recording
    camera.capture(connection, format='jpeg')
    # cleanup
    camera.close()
    connection.close()
    sock.close()


if __name__ == "__main__":
    # handle params
    parser = argparse.ArgumentParser()
    parser.add_argument("socket", help="Path to socket file to stream picture to")
    parser.add_argument("-n", "--night", action="store_true", default=False,
                        help="Whether to use cameras night vision enhancements")
    args = parser.parse_args()

    run(args)
