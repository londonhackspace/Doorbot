#!/usr/bin/python
import sys, os, time, re, socket, serial, urllib2, random
from datetime import datetime

sys.path.append('RFIDIOt-0.1x') # use local copy for stability
import RFIDIOtconfig

cardFile = 'cardtable.dat'

mTime = 0
cards = {}
currentCard = ''


def reloadCardTable():
    global mTime
    global cards

    try:
        currentMtime = os.path.getmtime(cardFile)
    except IOError, e:
        print e    

    if mTime != currentMtime:
        print "Loading card table, mtime %d" % currentMtime
        mTime = currentMtime
        cards = {};

        file = open(cardFile)

        regex = re.compile("^([^\s]+)\s*((?:[^\s]| )+)?$")
        for n, line in enumerate(file):
            entry, h, comment = line.partition('#')
            if not entry.strip():
                continue

            match = regex.match(entry)
            if match:
                id, name = match.groups()
                cards[id] = name
            else:
                print 'Invalid entry at line %d' % n

        print 'Loaded %d cards' % len(cards)


def checkForCard(card, ser):

    global currentCard

    if card.select():
        if currentCard == '' or currentCard != card.uid:
            currentCard = card.uid
            reloadCardTable()

            if currentCard in cards:
                print '%s: authorised %s as %s' % \
                    (datetime.now(), currentCard, cards[currentCard])

                ser.write("1"); # Trigger door relay

                broadcast('RFID', currentCard, cards[card.uid])

            else:
                print '%s: %s not authorised' % (datetime.now(), currentCard)
                broadcast('RFID', currentCard, '')

                ser.write("4"); # Red on
                ser.write("6"); # Piezo (Sleeps on the arduino for 3s)
                ser.write("5"); # Red off

            time.sleep(2) # To avoid read bounces if the card is _just_ in range

        else:
            currentCard = ''

    time.sleep(0.2)


def checkForSerial(ser):

    if ser.inWaiting() > 0:
        line = ser.readline()
        print 'Response from serial: %s' % line

        if line.startswith("1"):
            broadcast('BELL', '', '')

            ser.write("2"); # Green on
            ser.write("6"); # Piezo (Sleeps on the arduino for 3s)
            ser.write("3"); # Green off


def broadcast(event, card, name):

    try:
        print "Broadcasting %s to network" % event

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        data = "%s\n%s\n%s" % (event, card, name)
        s.sendto(data, ('<broadcast>', 50000))

    except Exception, e:
        pass



if __name__ == "__main__":

    reloadCardTable()
    broadcast('START', '', '')

    while True:

        try:
            card = RFIDIOtconfig.card
            ser = serial.Serial("/dev/ttyUSB0", 9600)

            while True:
                checkForCard(card, ser)
                checkForSerial(ser)

        except (serial.SerialException, serial.SerialTimeoutException), e:
            print e
            ser.close()

        except Exception, e:
            print e
            os._exit(True)
