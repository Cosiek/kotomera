#!/usr/bin/env python3
# encoding: utf-8

import socket
import sys
import time

from picamera import PiCamera


class Inspector:

    def __init__(self):
        self.min = 1000000000
        self.max = 0
        self.counter = 0

    def write(self, data):
        self.counter += 1
        l = len(data)
        self.min = min(self.min, l)
        self.max = max(self.max, l)
        print(self.counter, self.min, l, self.max)
        if l < 50:
            print("\t", data)


def run():
    # establish socket connection
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(sys.argv[1])
    connection = sock.makefile('wb')
    # get a camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 24
    # start recording
    #inspector = Inspector()
    camera.start_recording(connection, format='h264')
    #camera.start_recording(inspector, format='h264')
    i = 0
    while i < 6:
        #camera.wait_recording(10)
        time.sleep(10)
        i += 1
    camera.stop_recording()
    #    break
    connection.close()
    sock.close()


run()
