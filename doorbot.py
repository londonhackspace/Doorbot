#!/usr/bin/env python
import sys, os, time, serial, ConfigParser, json, logging
import argparse
from logging.handlers import SysLogHandler
from announcer import *
from relay import *
from RFUID import rfid


def ConfigObject(name):
    clsname = config.get('doorbot', name)
    cls = globals()[clsname]
    params = dict(config.items(clsname))
    return cls(**params)


class Doorbot(object):
    def __init__(self):
        self.mTime = 0
        self.lastCard = None
        self.cards = {}
        self.cardFile = config.get('doorbot', 'cardfile')
        self.relay = ConfigObject('relay')
        self.announcer = ConfigObject('announcer')
        self.reader = None

    def reload_cards(self):
        try:
            currentMtime = os.path.getmtime(self.cardFile)
        except IOError, e:
            logging.critical('Cannot read card file: %s', e)
            raise

        if self.mTime != currentMtime:

            logging.debug('Loading card table, mtime %d', currentMtime)
            self.mTime = 0
            newCards = {}

            with open(self.cardFile) as f:
                users = json.load(f)

            for user in users:
                if user.get('subscribed', True) == True:
                    for card in user['cards']:
                      card = card.encode('utf-8').upper()
                      nick = user['nick'].encode('utf-8')
                      newCards[card] = nick

            self.cards = newCards
            self.mTime = currentMtime
            logging.info('Loaded %d cards', len(self.cards))

    def check_card(self):
        try:
            for tag in self.reader.pn532.scan():
                uid = tag.uid.upper()
                if self.lastCard == uid:
                    return
                self.on_card(uid)
                self.lastCard = uid

        except rfid.NoCardException:
            self.lastCard = None
            return

    def on_card(self, uid):
        self.reload_cards()

        try:
            person = self.cards[uid]
            logging.info('%s authorised as %s', uid, person)
            self.reader.green_on()

            logging.debug('Triggering door relay')
            self.relay.openDoor(config.getfloat('doorbot', 'open_duration'))

            if args.foreground:
                logging.info('Would announce to network')
            else:
                logging.info('Announcing to network')
                self.announcer.send('RFID', uid, person)

        except KeyError, e:
            logging.warn('%s not authorised', uid)
            self.reader.red_on()

            if hasattr(self.relay, 'flashBad'):
                logging.debug('Sending unauthorised flash')
                self.relay.flashBad()

            if args.foreground:
                logging.info('Would announce failure to network')
            else:
                logging.info('Announcing failure to network')
                self.announcer.send('RFID', uid, '')

        logging.debug('Sleeping to avoid bounce')
        time.sleep(2) # To avoid read bounces if the card is _just_ in range


    def run(self):
        self.reload_cards()
        if args.foreground:
            logging.info('Would announce start')
        else:
            logging.info('Announcing start')
            self.announcer.send('START', '', '')

        logging.debug('Starting outer loop')
        # If the reader or relay disappears temporarily, we can recover safely
        while True:
            try:
                self.reader = rfid.Pcsc.reader()
                self.reader.open()
                logging.info('PCSC firmware: %s', self.reader.pn532.firmware())
                self.relay.connect()

            except Exception, e:
                logging.critical('Error during initialisation: %s', e)
                raise

            else:
                self.main_loop()

                # If it was working, give it some time to settle
                time.sleep(5)

            finally:
                self.relay.disconnect()
                self.reader.close()

    def main_loop(self):
        logging.debug('Starting main loop')
        while True:
            try:
                self.check_card()
                self.reader.leds_off()
                time.sleep(0.2)

                if self.relay.checkBell():
                    logging.info("Doorbell pressed")
                    self.relay.red_on()

                    if not args.foreground:
                        self.announcer.send('BELL', '', '')
                    if hasattr(self.relay, 'flashOK'):
                        self.relay.flashOK()

                    # Wait for button to be released
                    time.sleep(0.5)


            except (serial.SerialException, serial.SerialTimeoutException), e:
                logging.warn('Serial error during poll: %s', e)
                return

            except Exception, e:
                logging.critical('Unexpected error during poll: %s', e)
                # sometimes the card reader goes away and dosn't come back, if so we
                # get "Error PC01 selecting card" forever, i don't think we can fix
                # this from here, so lets just quit

                # we could send a message to the net that we've failed.
                # but the announcer api is clunky, i can has json re-write pls?
                raise



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
    from daemon import DaemonContext
    from pidfile import PidFile
    daemon = DaemonContext(pidfile=PidFile("/var/run/doorbot.pid"))
    daemon.open()

    logging.info('Daemonised doorbot')


if __name__ == "__main__":
    args = parse_args()

    open_config()
    set_logger()

    if not args.foreground:
        daemonise()

    doorbot = Doorbot()
    try:
        doorbot.run()

    # Top-level handlers because we're daemonised
    except Exception, e:
        logging.exception("Exception in main loop: %s" % e)
    except:
        logging.exception("Non-Exception caught")


