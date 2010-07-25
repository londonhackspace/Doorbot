#!/usr/bin/python
import sys, os, time, re, socket, serial, urllib2

cardFile = 'cardtable.dat'

# We're binding against the local copy for stability
sys.path.append('RFIDIOt-0.1x')
import RFIDIOtconfig

try:
    card = RFIDIOtconfig.card
except:
    os._exit(True)


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
                cards[matches[0][0]] = matches[0][1]

    return cards


mTime = 0
cards = {}
currentCard = ''

ser = serial.Serial("/dev/ttyUSB0", 19200)

while (True):
    if card.select():
        if currentCard == '' or currentCard != card.uid:
            currentCard = card.uid
            cards = reloadCardTable(cards)

            if currentCard in cards:
                ser.write("1");

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('babbage.lan', 12345))
                s.send("%s opened the hackspace door." % cards[card.uid])
                s.close()

                urllib2.urlopen('http://babbage.lan:8000/_/255,255,255?restoreAfter=10')

    else:
        currentCard = ''

    time.sleep(0.2)
