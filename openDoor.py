#!/usr/bin/env python

import serial, sys, time

try:
  port = sys.argv[1]
except:
  port = '/dev/ttyUSB0'
print 'Using port %s' % port

ser = serial.Serial(port, 9600)
time.sleep(2) # Wait for it to reboot

ser.write('1')
time.sleep(0.5)
print 'Response: %s' % ser.readline()

ser.close()
