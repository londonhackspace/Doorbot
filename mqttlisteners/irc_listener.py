# Heavily inspired by the old broadcast listener

from MQTTDoorbotListener import MQTTDoorbotListener
import random
import datetime
import time
import unicodedata
import pickle
import os
import socket

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

class IRCDoorbotListener(MQTTDoorbotListener):

    def __init__(self):
        super().__init__()
        self.topic = self.config['irc']['topic']
        self.summary_topic = self.config['irc']['summary_topic']
        self.lastMessage = None
        self.dupeMessages = 0

    def on_card(self, card_id, name, door, gladosfile):
        if not door.getboolean('announce', True):
            return

        if name == 'Inspector Sands':
            msg = "%s reported to %s" % (fix_rtl(strip_string(name)), door['name'])
        else:
            msg = "%s opened %s" % (fix_rtl(strip_string(name)), door['name'])

        lastseen = {}

        picklefile = self.config.get('lastseen', 'picklefile')

        if os.path.exists(picklefile):
            lastseen = pickle.load(open(picklefile, 'rb'))

        summary = False

        try:
            d = lastseen[name.lower()]
        except KeyError:
            pass
        else:
            ago = datetime.datetime.now() - d
            if ago > datetime.timedelta(0, 60):
              msg = '%s (Last seen %s ago)' % (msg, untilmsg(ago))
            # also announce to the summary channel if ago is longer than an hour ao
            if ago > datetime.timedelta(0, 3600):
                summary = True

        if name == 'ragey':
            msg = "RAGEY SMASH PUNY DOOR, RAGEY RAGE ENTER HACKSPACE NOW"

        self.send_message(msg, summary)


    def on_unknown_card(self, card_id, door):
        self.send_message("Unknown card presented to %s" % (door['name'],))

    def on_start(self, door):
        self.send_message(get_welcome(door.get('welcomename', door['name'])))

    def on_alive(self, door):
        pass

    def on_denied(self, card_id, name, door):
        self.send_message("denied access to user at door %s" % (door['name'],))

    def on_bell(self, door):
        today = datetime.date.today()
        m, d = today.month, today.day
        if (m, d) >= (12, 24) and (m, d) <= (12, 31):
            dingdong = 'DING DONG MERRILY ON HIGH, DOOR BELL!'
        else:
            dingdong = 'DING DONG, DOOR BELL!'
        self.send_message("%s: %s" % (door['name'], dingdong), True)

    def send_message(self, message, summary=False):
        # add the channel name to the start
        if summary:
            # every summary message becomes a normal message as well
            self.send_message(message, False)
            message = self.summary_topic + " " + message
        else:
            message = self.topic + " " + message
        print('%s %r' % (time.strftime('%Y-%m-%d %H:%M:%S'), message))
        if message == self.lastMessage:
            if time.time() - self.lastTime < 5:
                print('Suppressing duplicate message')
                self.dupeMessages += 1
                return
            elif self.dupeMessages > 1:
                message = '%s (repeated %s times)' % (message, self.dupeMessages)

        # Otherwise, drop any outstanding dupes for now

        self.lastMessage = message
        self.lastTime = time.time()
        self.dupeMessages = 0

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            server = self.config.get('irc', 'irccat')
            port = self.config.getint('irc', 'irccat_port')
            s.connect((server, port))
            s.send(message.encode('utf-8'))
            s.close()
        except Exception as e:
            print('Exception in main loop: %s' % repr(e))

if __name__ == '__main__':
    dbl = IRCDoorbotListener()
    dbl.run()