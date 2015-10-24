#!/usr/bin/env python
import sys
from socket import *

def usage():
    """ Print some usage info """
    print "Usage: " + sys.argv[0] + " [BELL|RFID|TRIGGER]"

if len(sys.argv) < 2:
    usage()
    sys.exit(1)

cmd = sys.argv[1].upper()
if cmd == "BELL":
        print "Ringing the doorbell..."
        data = "BELL\n\n"
elif cmd == "RFID":
        if len(sys.argv) != 3:
            print "Usage: %s RFID [cardid]" % (sys.argv[0])
            sys.exit(1)
        # do RFID stuff
        cardid = sys.argv[2]
        print "Pretending user with cardid [%s] presented their card" % (cardid)
        data = "RFID\n%s\n" % (cardid)
elif cmd == "TRIGGER":
        if len(sys.argv) != 3:
            print "Usage: %s TRIGGER [filename]" % (sys.argv[0])
            sys.exit(1)
        # Trigger an audio file
        filename = sys.argv[2]
        print "Triggering audio file [%s]" % (filename)
        data = "TRIGGER\n%s\n" % (filename)
else:
        print "Unknown command [%s]" % (cmd)
        usage()
        sys.exit(1)

s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

s.sendto(data, ('<broadcast>', 50002))
