#!/usr/bin/python
import sys, os, time, re, socket, serial, urllib2, random
from datetime import datetime
import logging
import json

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
logging.info('Starting doorbot')

try:
    sys.path.append('RFIDIOt-0.1x') # use local copy for stability
    import RFIDIOtconfig

except Exception, e:
    logging.critical('Error importing RFIDIOt: %s', e)
    sys.exit(1)

cardFile = 'carddb.json'
mTime = 0
cards = {}

currentCard = ''


def reloadCardTable():
    global mTime
    global cards

    try:
        currentMtime = os.path.getmtime(cardFile)
    except IOError, e:
        logging.critical('Cannot read card file: %s', e)
        raise

    if mTime != currentMtime:

        logging.debug('Loading card table, mtime %d', currentMtime)
        mTime = currentMtime
        cards = {}

        file = open(cardFile)

        users = json.load(file)

        for user in users:
            for card in user['cards']:
              card = card.encode('utf-8')
              nick = user['nick'].encode('utf-8')
              cards[card] = nick

        logging.info('Loaded %d cards', len(cards))


def checkForCard(card, ser):

    global currentCard

    if not card.select():
        # Yeah, we really should rewrite RFIDIOt
        if card.errorcode != card.PCSC_NO_CARD:
            raise Exception('Error %s selecting card' % card.errorcode)

    else:
        if currentCard == '' or currentCard != card.uid:
            currentCard = card.uid
            reloadCardTable()

            if currentCard in cards:
                logging.info('%s authorised as %s',
                    currentCard, cards[currentCard])

                logging.debug('Triggering door relay')
                ser.write("1");

                logging.debug('Broadcasting to network')
                broadcast('RFID', currentCard, cards[card.uid])

            else:
                logging.warn('%s not authorised', currentCard)

                logging.debug('Sending unauthorised flash')
                ser.write("4"); # Red on
                ser.write("6"); # Piezo (Sleeps on the arduino for 3s)
                ser.write("5"); # Red off

                broadcast('RFID', currentCard, '')

            time.sleep(2) # To avoid read bounces if the card is _just_ in range

        else:
            currentCard = ''


def checkForSerial(ser):

    if ser.inWaiting() > 0:
        line = ser.readline()
        logging.debug('Response from serial: %s', line)

        if line.startswith("1"):
            logging.info('Doorbell pressed')
            broadcast('BELL', '', '')

            ser.write("2"); # Green on
            ser.write("6"); # Piezo (Sleeps on the arduino for 3s)
            ser.write("3"); # Green off


def broadcast(event, card, name):

    try:
        logging.debug('Broadcasting %s to network', event)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        data = "%s\n%s\n%s" % (event, card, name)
        s.sendto(data, ('<broadcast>', 50000))

    except Exception, e:
        logging.warn('Exception during broadcast: %s', e)


if __name__ == "__main__":

    reloadCardTable()
    logging.info('Announcing start')
    broadcast('START', '', '')

    while True:

        logging.debug('Starting main loop')

        ser = None
        try:
            card = RFIDIOtconfig.card
            ser = serial.Serial("/dev/ttyUSB0", 9600)

        except (serial.SerialException, serial.SerialTimeoutException), e:
            logging.warn('Serial error during initialisation: %s', e)
            break

        except Exception, e:
            logging.critical('Unexpected error during initialisation: %s', e)
            break


        try:
            while True:
                checkForCard(card, ser)
                time.sleep(0.2)
                checkForSerial(ser)

        except (serial.SerialException, serial.SerialTimeoutException), e:
            logging.warn('Serial error during poll: %s', e)
            if ser:
              ser.close()

        except Exception, e:
            logging.critical('Unexpected error during poll: %s', e)

        # If it was working, give it some time to settle
        time.sleep(5)

    os._exit(True) # Otherwise RFIDIOt interferes in cleanup
