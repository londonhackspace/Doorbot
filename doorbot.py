#!/usr/bin/env python
import sys, os, time, serial
import ConfigParser
import logging
import json
from announcer import *
from relay import *

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
logging.info('Starting doorbot')

try:
    sys.path.append('RFIDIOt-0.1x') # use local copy for stability
    import RFIDIOtconfig

except Exception, e:
    logging.critical('Error importing RFIDIOt: %s', e)
    sys.exit(1)

config = ConfigParser.ConfigParser()
config.read((
    'doorbot.conf',
    sys.path[0] + '/doorbot.conf',
    '/etc/doorbot.conf'
))

cardFile = config.get('doorbot', 'cardfile')
mTime = 0
cards = {}

currentCard = ''

def ConfigObject(name):
    clsname = config.get('doorbot', name)
    cls = globals()[clsname]
    params = dict(config.items(clsname))
    return cls(**params)


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
            if user.get('subscribed', True) == True:
                for card in user['cards']:
                  card = card.encode('utf-8')
                  nick = user['nick'].encode('utf-8')
                  cards[card] = nick

        logging.info('Loaded %d cards', len(cards))


def checkForCard():

    global currentCard

    if not card.select():
        # Yeah, we really should rewrite RFIDIOt
        if card.errorcode != card.PCSC_NO_CARD:
            raise Exception('Error %s selecting card' % card.errorcode)

        return

    if currentCard == '' or currentCard != card.uid:
        currentCard = card.uid
        reloadCardTable()

        if currentCard in cards:
            logging.info('%s authorised as %s',
                currentCard, cards[currentCard])

            logging.debug('Triggering door relay')
            relay.openDoor()

            logging.debug('Announcing to network')
            announcer.send('RFID', currentCard, cards[card.uid])

        else:
            logging.warn('%s not authorised', currentCard)

            if hasattr(relay, 'flashRed'):
                logging.debug('Sending unauthorised flash')
                relay.flashRed()

            announcer.send('RFID', currentCard, '')

        time.sleep(2) # To avoid read bounces if the card is _just_ in range

    else:
        currentCard = ''


def run():
    global card
    global relay
    global announcer

    announcer = ConfigObject('announcer')
    relay = ConfigObject('relay')

    reloadCardTable()
    logging.info('Announcing start')
    announcer.send('START', '', '')

    while True:
        logging.debug('Starting main loop')

        try:
            card = RFIDIOtconfig.card
            relay.connect()

        except (serial.SerialException, serial.SerialTimeoutException), e:
            logging.warn('Serial error during initialisation: %s', e)
            break

        except Exception, e:
            logging.critical('Unexpected error during initialisation: %s', e)
            break


        try:
            while True:
                checkForCard()
                time.sleep(0.2)

                if relay.checkBell():
                    announcer.send('BELL', '', '')
                    if hasattr(relay, 'flashGreen'):
                        relay.flashGreen()

                    # Wait for button to be released
                    time.sleep(0.5)


        except (serial.SerialException, serial.SerialTimeoutException), e:
            logging.warn('Serial error during poll: %s', e)
            relay.disconnect()

        except Exception, e:
            logging.critical('Unexpected error during poll: %s', e)

        # If it was working, give it some time to settle
        time.sleep(5)

    os._exit(True) # Otherwise RFIDIOt interferes in cleanup


if __name__ == "__main__":
    run()

