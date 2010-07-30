#!/usr/bin/python
import sys, os, time, re, socket, serial, urllib2
from datetime import datetime

cardFile = 'cardtable.dat'

# We're binding against the local copy for stability
sys.path.append('RFIDIOt-0.1x')
import RFIDIOtconfig

try:
    card = RFIDIOtconfig.card
except:
    os._exit(True)

ser = serial.Serial("/dev/ttyUSB0", 9600)

def reloadCardTable(cards):
    global mTime
    currentMtime = os.path.getmtime(cardFile)

    if mTime != currentMtime:
        print "Loading card table, mtime %d" % currentMtime
        mTime = currentMtime
        cards = {};

        regex = re.compile("^([^#\n ]+)\s*([^#\n ]+)?$")

        file = open(cardFile)
        for line in file:
            if regex.match(line):
                matches = regex.findall(line)
                id, name = matches[0]
                cards[id] = name

        print 'Loaded card table'

    return cards


mTime = 0
cards = {}
currentCard = ''


while (True):
    if card.select():
        if currentCard == '' or currentCard != card.uid:
            currentCard = card.uid
            cards = reloadCardTable(cards)

            if currentCard in cards:
                print '%s: authorised %s as %s' % \
                        (datetime.now(), currentCard, cards[currentCard])

                ser.write("1");

                try:
                    print 'Logging to irccat on babbage'
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(('172.31.24.101', 12345))
                    s.send("%s opened the hackspace door." % cards[card.uid])
                    s.close()
                except Exception:
                    pass

                try:
                    print 'Turning on lights'
                    urllib2.urlopen('http://172.31.24.101:8000/_/255,255,255?restoreAfter=10')
                except Exception:
                    pass

                print 'Entrance complete'

            else:
                print '%s: %s not authorised' % (datetime.now(), currentCard)
    else:
        currentCard = ''

    time.sleep(0.2)
