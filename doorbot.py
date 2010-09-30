#!/usr/bin/python
import sys, os, time, re, socket, serial, urllib2, random
from datetime import datetime

sys.path.append('RFIDIOt-0.1x') # use local copy for stability
import RFIDIOtconfig


cardFile = 'cardtable.dat'

mTime = 0
cards = {}
currentCard = ''


def ircsay(msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('172.31.24.101', 12345))
    s.send(msg)
    s.close()


def welcome():
    print 'This is doorbot'

    welcomes = [
        'This is doorbot and welcome to you who have come to doorbot',
        'Anything is possible with doorbot',
        'The infinite is possible with doorbot',
        'The unattainable is unknown with doorbot',
        'You can do anything with doorbot',
    ]
    welcomes += ['This is doorbot', 'Welcome to doorbot'] * 10
    ircsay(random.choice(welcomes))


def reloadCardTable():
    global mTime
    global cards

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


def checkForCard(card, ser):

    global currentCard

    if card.select():
	if currentCard == '' or currentCard != card.uid:
	    currentCard = card.uid
	    reloadCardTable()

	    if currentCard in cards:
		print '%s: authorised %s as %s' % \
			(datetime.now(), currentCard, cards[currentCard])

		ser.write("1");

		try:
		    print 'Logging to IRC'
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
		    urllib2.urlopen('http://172.31.24.101:8020/'
                            '%s%%20just%%20opened%%20the%%20door?restoreAfter=10' % cards[card.uid])
		except Exception:
		    pass

		print 'Entrance complete'

	    else:
		print '%s: %s not authorised' % (datetime.now(), currentCard)
    else:
	currentCard = ''

    time.sleep(0.2)


def checkForSerial(ser):

    if ser.inWaiting() > 0:
        line = ser.readline()
        print 'Response from serial: %s' % line
        if line.startswith == "1":
            try:
                ircsay("BING BONG! Someone's at the door: http://hack.rs:8003")
            except Exception, e:
                pass

            try:
                urllib2.urlopen('http://172.31.24.101:8020/'
                            'BING BONG-DOOR BELL?restoreAfter=10')
            except Exception, e:
                pass

            ser.write("4");
            time.sleep(5)
            ser.write("5");



welcomed = False

while True:

    try:
        card = RFIDIOtconfig.card
        ser = serial.Serial("/dev/ttyUSB0", 9600)

        if not welcomed:
            try:
                welcome()
                welcomed = True
            except Exception:
                pass

        while True:
            checkForCard(card, ser)
            checkForSerial(ser)

    except (serial.SerialException, serial.SerialTimeoutException), e:
        print e
        ser.close()

    except Exception, e:
        print e
        os._exit(True)


