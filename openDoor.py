#!/usr/bin/env python

import serial, sys, time

try:
  port = sys.argv[1]
except:
  port = '/dev/ttyUSB0'
print 'Using port %s' % port

ser = serial.Serial(port, 9600)
print 'Opened. Waiting for reboot...'
time.sleep(3) # Wait for it to reboot

print 'Opening door...'
ser.write("\xff\x01\x01")
time.sleep(0.5)
ser.write("\xff\x01\x00")
print 'Response: %s' % ser.readline()

ser.close()
