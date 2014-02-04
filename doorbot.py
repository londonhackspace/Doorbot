#!/usr/bin/env python
import sys, os, time, serial, ConfigParser, json, logging, daemon, traceback
from logging.handlers import SysLogHandler
from pidfile import PidFile
from announcer import *
from relay import *


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

            if hasattr(relay, 'flashBad'):
                logging.debug('Sending unauthorised flash')
                relay.flashBad()

            announcer.send('RFID', currentCard, '')

        time.sleep(2) # To avoid read bounces if the card is _just_ in range

    else:
        currentCard = ''


def run():
    global card
    global relay
    global announcer

    logging.info('in run')
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
                    logging.info("Doorbell pressed")
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

    os._exit(True) # Otherwise RFIDIOt interferes in cleanup

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read((
        'doorbot.conf',
        sys.path[0] + '/doorbot.conf',
        '/etc/doorbot.conf'
        ))

    logfac = config.get('doorbot', 'logfacility')
    logfac = SysLogHandler.facility_names[logfac]
    logger = logging.root
    logger.setLevel(logging.DEBUG)
    syslog = SysLogHandler(address='/dev/log', facility=logfac)
    formatter = logging.Formatter('Doorbot[%(process)d]: %(levelname)-8s %(message)s')
    syslog.setFormatter(formatter)
    logger.addHandler(syslog)

    logging.info('Starting doorbot')
    logging.info(sys.path[0])

    try:
        cardFile = config.get('doorbot', 'cardfile')
        mTime = 0
        cards = {}
        currentCard = ''
    except:
        logging.exception('importing cards: ')
        sys.exit(1)

    try:
        d = daemon.DaemonContext(pidfile=PidFile("/var/run/doorbot.pid"))
        d.open()
    except:
        logging.exception('daemonising: ')
        sys.exit(1)

    logging.info('Daemonised doorbot')

    def my_excepthook(excType, excValue, traceback, logger=logger):
        logger.error("Logging an uncaught exception",
            exc_info=(excType, excValue, traceback))

    sys.excepthook = my_excepthook  

    try:
        sys.path.append(sys.path[0] + '/RFIDIOt-0.1x') # use local copy for stability
        import RFIDIOtconfig

    except Exception, e:
        logging.exception("Error importing RFIDIOt:")
        sys.exit(1)

    try:
        run()
    except:
        logging.exception("running: ")
        sys.exit(1)

