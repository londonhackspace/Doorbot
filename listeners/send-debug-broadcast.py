#!/usr/bin/env python
import sys
from socket import *

if (sys.argv[1] not in ('BELL', 'RFID')):
    print "Unknown event type, valid types are (RFID, BELL)"
    sys.exit(0)

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

data = "\n".join(sys.argv[1:])
s.sendto(data, ('<broadcast>', 50000))
