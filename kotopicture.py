#!/usr/bin/env python3
# encoding: utf-8

import socket
import sys

from picamera import PiCamera


def run():
    # establish socket connection
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(sys.argv[1])
    connection = sock.makefile('wb')
    # get a camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    # start recording
    camera.capture(connection, format='jpeg')
    # cleanup
    connection.close()
    sock.close()


if __name__ == "__main__":
    run()