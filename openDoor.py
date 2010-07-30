#!/usr/bin/env python

import serial, sys

try:
  port = sys.argv[1]
except:
  port = '/dev/ttyUSB0'

ser = serial.Serial(port, 9600)
ser.write('1')
ser.close()
