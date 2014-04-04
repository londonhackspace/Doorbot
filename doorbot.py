#!/usr/bin/env python
import sys, os, time, serial, ConfigParser, json, logging
from daemon import DaemonContext
import argparse
from logging.handlers import SysLogHandler
from pidfile import PidFile
from announcer import *
from relay import *
from RFUID import rfid

# TODO: get rid of some of these globals
mTime = 0
currentCard = None
cards = {}


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
        mTime = 0
        newCards = {}

        file = open(cardFile)

        users = json.load(file)

        for user in users:
            if user.get('subscribed', True) == True:
                for card in user['cards']:
                  card = card.encode('utf-8')
                  nick = user['nick'].encode('utf-8')
                  newCards[card] = nick

        cards = newCards
        mTime = currentMtime
        logging.info('Loaded %d cards', len(cards))


def checkForCard():

    global currentCard
    global config

    try:
        with rfid.Pcsc.reader() as reader:
            for tag in reader.pn532.scan():
                uid = tag.uid.upper()
                break
    except rfid.NoCardException:
        currentCard = None
        return

    if currentCard == uid:
        return

    currentCard = uid
    reloadCardTable()

    if currentCard in cards:
        logging.info('%s authorised as %s',
            currentCard, cards[currentCard])

        logging.debug('Triggering door relay')
        relay.openDoor(config.getfloat('doorbot', 'open_duration', 2))

        if args.foreground:
            logging.info('Would announce to network')
        else:
            logging.info('Announcing to network')
            announcer.send('RFID', currentCard, cards[uid])

    else:
        logging.warn('%s not authorised', currentCard)

        if hasattr(relay, 'flashBad'):
            logging.debug('Sending unauthorised flash')
            relay.flashBad()

        if args.foreground:
            logging.info('Would announce failure to network')
        else:
            logging.info('Announcing failure to network')
            announcer.send('RFID', currentCard, '')

    time.sleep(2) # To avoid read bounces if the card is _just_ in range


def run():
    global relay
    global announcer
    global cardFile

    if not args.foreground:
        daemonise()

    cardFile = config.get('doorbot', 'cardfile')
    announcer = ConfigObject('announcer')
    relay = ConfigObject('relay')

    reloadCardTable()
    if args.foreground:
        logging.info('Would announce start')
    else:
        logging.info('Announcing start')
        announcer.send('START', '', '')

    while True:
        logging.debug('Starting main loop')

        try:
            # TODO: keep this reader for checkForCard
            with rfid.Pcsc.reader() as reader:
                logging.info('PCSC firmware: %s', reader.pn532.firmware())

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
                    logging.info("Doorbell pressed")
                    if not args.foreground:
                        announcer.send('BELL', '', '')
                    if hasattr(relay, 'flashOK'):
                        relay.flashOK()

                    # Wait for button to be released
                    time.sleep(0.5)


        except (serial.SerialException, serial.SerialTimeoutException), e:
            logging.warn('Serial error during poll: %s', e)
            relay.disconnect()

        except Exception, e:
            logging.critical('Unexpected error during poll: %s', e)
            # sometimes the card reader goes away and dosn't come back, if so we
            # get "Error PC01 selecting card" forever, i don't think we can fix
            # this from here, so lets just quit
            
            # we could send a message to the net that we've failed.
            # but the announcer api is clunky, i can has json re-write pls?
            
            # using this method to quit cos of the message below
            # no idea if thats a good idea.
            os._exit(True)
            

        # If it was working, give it some time to settle
        time.sleep(5)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--foreground', action='store_true')
    args = parser.parse_args()
    return args

def open_config():
    global config
    config = ConfigParser.ConfigParser()
    config.read((
        'doorbot.conf',
        sys.path[0] + '/doorbot.conf',
        '/etc/doorbot.conf'
    ))

def set_logger():
    if args.foreground:
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
    else:
        logfac = config.get('doorbot', 'logfacility')
        logfac = SysLogHandler.facility_names[logfac]
        logger = logging.root
        logger.setLevel(logging.DEBUG)
        syslog = SysLogHandler(address='/dev/log', facility=logfac)
        formatter = logging.Formatter('Doorbot[%(process)d]: %(levelname)-8s %(message)s')
        syslog.setFormatter(formatter)
        logger.addHandler(syslog)

def daemonise():
    daemon = DaemonContext(pidfile=PidFile("/var/run/doorbot.pid"))
    daemon.open()

    logging.info('Daemonised doorbot')


if __name__ == "__main__":
    args = parse_args()

    open_config()
    set_logger()

    try:
        run()
    except Exception, e:
        logging.exception("Exception in main loop")
    except:
        logging.exception("Non-Exception caught")


