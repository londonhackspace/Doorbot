#!/usr/bin/env python
import socket, pickle
import os, random
import datetime
import unicodedata
import argparse
from DoorbotListener import DoorbotListener, get_doorbot, config

def dayordinal(day):
  if 4 <= day <= 20 or 24 <= day <= 30:
    suffix = 'th'
  else:
    suffix = ['st', 'nd', 'rd'][day % 10 - 1]
  return '%d%s' % (day, suffix)

def untilmsg(until):
    hours, seconds = divmod(until.seconds, 3600)
    days = until.days
    d_s = '' if days == 1 else 's'
    h_s = '' if hours == 1 else 's'
    
    if hours ==0 and days == 0:
        return '%s minutes' % int(seconds/60)
    elif days == 0:
        return '%s hour%s' % (hours, h_s)
    elif hours == 0:
        return '%s day%s' % (days, d_s)
    else:
        return '%s day%s, %s hour%s' % (days, d_s, hours, h_s)

def get_welcome(place):
    welcomes = [
        'This is %(place)s and welcome to you who have come to %(place)s',
        'Anything is possible with %(place)s',
        'The infinite is possible with %(place)s',
        'The unattainable is unknown with %(place)s',
    ]
    welcomes += ['This is %(place)s', 'Welcome to %(place)s'] * 10

    welcome = random.choice(welcomes) % {'place': place}
    return welcome

def strip_string(string):
  """Cleans a string based on a whitelist of printable unicode categories
 
  You can find a full list of categories here:
  http://www.fileformat.info/info/unicode/category/index.htm
  """
  letters     = ('LC', 'Ll', 'Lm', 'Lo', 'Lt', 'Lu')
  numbers     = ('Nd', 'Nl', 'No')
  marks       = ('Mc', 'Me', 'Mn')
  punctuation = ('Pc', 'Pd', 'Pe', 'Pf', 'Pi', 'Po', 'Ps')
  symbol      = ('Sc', 'Sk', 'Sm', 'So')
  space       = ('Zs',)
 
  allowed_categories = letters + numbers + marks + punctuation + symbol + space
 
  return ''.join([ c for c in string if unicodedata.category(c) in allowed_categories ])

def fix_rtl(string):
  # If there are any strongly RTL chars, hint that we're already in an LTR context, and want to be afterwards
  rtl_chars = [c for c in string if unicodedata.bidirectional(c) in ['R', 'AL', 'RLE', 'RLO', 'RLI']]
  if rtl_chars:
    return u'\u200e' + string + u'\u200e'

  return string

def reload_lastseen():
    global lastseen
    lastseen = {}
    lastseenfile = config.get('lastseen', 'picklefile')
    if os.path.exists(lastseenfile):
        lastseen = pickle.load(open(lastseenfile))


class IrccatListener(DoorbotListener):
    def startup(self):
        self.sendMessage(get_welcome(this_doorbot.welcomename))

    def doorbell(self):
        today = datetime.date.today()
        m, d = today.month, today.day
        if (m, d) >= (12, 24) and (m, d) <= (12, 31):
            dingdong = 'DING DONG MERRILY ON HIGH, DOOR BELL!'
        else:
            dingdong = 'DING DONG, DOOR BELL!'
        msg = [dingdong]

        doorbot = get_doorbot(doorbotname)
        if hasattr(doorbot, 'camurl'):
            msg.append(doorbot.camurl)

        self.sendMessage(' '.join(msg))

    def doorOpened(self, serial, name):

        if name == 'Ragey':
            self.sendMessage("RAGEY SMASH PUNY DOOR, RAGEY RAGE ENTER HACKSPACE NOW")
            return

        doorbot = get_doorbot(doorbotname)

        openedmsg = u'%s opened %s.' % (
            fix_rtl(strip_string(name.decode('utf-8'))),
            doorbot.location,
        )
        msg = [openedmsg]

        reload_lastseen()
        try:
            d = lastseen[name.lower()]
        except KeyError:
            pass
        else:
            ago = datetime.datetime.now() - d
            if ago > datetime.timedelta(0, 60):
              msg.append('(Last seen %s ago)' % untilmsg(ago))

        self.sendMessage(' '.join(msg))

    def unknownCard(self, serial):

	print 'Unknown card: %s' % serial

        doorbot = get_doorbot(doorbotname)
        unknown_msg = "Unknown card presented at %s." % doorbot.location
        msg = ['#london-hack-space-dev', unknown_msg]

        if hasattr(doorbot, 'camurl'):
            msg.append(doorbot.camurl)

        self.sendMessage(' '.join(msg))

    def sendMessage(self, message):
        if not isinstance(message, unicode):
            message = message.decode('utf-8')

        print repr(message)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            server = config.get('irccat', 'server')
            port = config.getint('irccat', 'port')
            s.connect((server, port))
            s.send(message.encode('utf-8'))
            s.close()
        except Exception, e:
            print 'Exception in main loop: %s' % repr(e)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--doorbot', default='default')
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    # Once we start broadcasting the doorbot ID, we can just replace
    # this_doorbot.blah with a literal, or use default for now
    doorbotname = args.doorbot
    this_doorbot = get_doorbot(doorbotname)

    listener = IrccatListener()
    listener.listen(int(this_doorbot.port))

