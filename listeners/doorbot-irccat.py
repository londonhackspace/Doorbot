#!/usr/bin/env python
import DoorbotListener, socket, random, os, pickle, datetime, unicodedata

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

PICKLEFILE = '/usr/share/irccat/.lastseen.pickle'
location = 'the hackspace door'
welcomes = [
    'This is doorbot and welcome to you who have come to doorbot',
    'Anything is possible with doorbot',
    'The infinite is possible with doorbot',
    'The unattainable is unknown with doorbot',
]
welcomes += ['This is doorbot', 'Welcome to doorbot'] * 10


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


class IrccatListener(DoorbotListener.DoorbotListener):

    def startup(self):
        self.sendMessage(random.choice(welcomes))

    def doorbell(self):
        today = datetime.date.today()
        m, d = today.month, today.day
        if (m, d) >= (12, 24) and (m, d) <= (12, 31):
            msg = 'DING DONG MERRILY ON HIGH, DOOR BELL!'
        else:
            msg = 'DING DONG, DOOR BELL!'

        self.sendMessage(' '.join((
            msg,
            #'http://hack.rs/doorbell.jpg',
            'http://london.hackspace.org.uk/members/webcams.php?camera=3',
        )))

    def doorOpened(self, serial, name):

        lastseen = {}
        if os.path.exists(PICKLEFILE):
            lastseen = pickle.load(open(PICKLEFILE))

        try:
            d = lastseen[name.lower()]
        except KeyError:
            agomsg = ''
        else:
            ago = datetime.datetime.now() - d
            agomsg = ' (Last seen %s ago)' % untilmsg(ago)

        if name == 'Ragey':
            self.sendMessage("RAGEY SMASH PUNY DOOR, RAGEY RAGE ENTER HACKSPACE NOW")
            return

        self.sendMessage(u'\u200e%s opened %s.%s' % (
            strip_string(name.decode('utf-8')),
            location,
            agomsg,
        ))


    def unknownCard(self, serial):
        self.sendMessage("Unknown card presented at %s." % location)

    def sendMessage(self, message):
        if not isinstance(message, unicode):
            message = message.decode('utf-8')

        print repr(message)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect(('172.31.24.5', 12345))
            s.send(message.encode('utf-8'))
            s.close()
        except Exception, e:
            print 'Exception in main loop: %s' % repr(e)

if __name__ == '__main__':
	listener = IrccatListener()
	listener.listen()
