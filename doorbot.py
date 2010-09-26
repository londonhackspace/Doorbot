#!/usr/bin/python
import sys, os, time, re, socket, serial, urllib2, random
from datetime import datetime

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
                id, name = matches[0]
                cards[id] = name

        print 'Loaded card table'

    return cards

def ircsay(msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('172.31.24.101', 12345))
    s.send(msg)
    s.close()

mTime = 0
cards = {}
currentCard = ''

print 'This is doorbot'

#ircsay('This is doorbot')
welcomes = [
  'This is doorbot and welcome to you who have come to doorbot',
  'Anything is possible with doorbot',
  'The infinite is possible with doorbot',
  'The unattainable is unknown with doorbot',
  'You can do anything with doorbot',
]
welcomes += ['This is doorbot', 'Welcome to doorbot'] * 10
ircsay(random.choice(welcomes))

while (True):
    if card.select():
        if currentCard == '' or currentCard != card.uid:
            currentCard = card.uid
            cards = reloadCardTable(cards)

            if currentCard in cards:
                print '%s: authorised %s as %s' % \
                        (datetime.now(), currentCard, cards[currentCard])

                ser = serial.Serial("/dev/ttyUSB0", 9600)
                ser.write("1");
                ser.close();

                try:
                    print 'Logging to irccat on babbage'
                    ircsay("%s opened the hackspace door." % cards[card.uid])
                except Exception:
                    pass

                try:
                    print 'Turning on lights'
                    urllib2.urlopen('http://172.31.24.101:8000/_/255,255,255?restoreAfter=10')
                except Exception:
                    pass

                try:
                    print 'Displaying on board'
                    #import pdb;pdb.set_trace()
                    urllib2.urlopen('http://172.31.24.101:8020/%s%%20just%%20opened%%20the%%20door?restoreAfter=10' % cards[card.uid])
                except Exception:
                    pass

                print 'Entrance complete'

            else:
                print '%s: %s not authorised' % (datetime.now(), currentCard)
    else:
        currentCard = ''

    time.sleep(0.2)
