#!/usr/bin/env python
import DoorbotListener, socket, random, os, pickle, datetime

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


class IrccatListener(DoorbotListener.DoorbotListener):

    def startup(self):
        welcomes = [
            'This is doorbot and welcome to you who have come to doorbot',
            'Anything is possible with doorbot',
            'The infinite is possible with doorbot',
            'The unattainable is unknown with doorbot',
            'You can do anything with doorbot',
        ]
        welcomes += ['This is doorbot', 'Welcome to doorbot'] * 10
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
            'http://hack.rs/doorbell.jpg',
            'http://london.hackspace.org.uk/members/webcams.php?camera=3',
        )))

    def doorOpened(self, serial, name):

        lastseen = {}
        if os.path.exists(PICKLEFILE):
            lastseen = pickle.load(open(PICKLEFILE))

        try:
            d = lastseen[name.lower()]

            self.sendMessage(
                "%s opened the hackspace door. (Last seen %s ago)" % (
                    name,
                    untilmsg(datetime.datetime.now() - d)
                )
            )

        except KeyError:
            self.sendMessage("%s opened the hackspace door." % name)


    def unknownCard(self, serial):
        self.sendMessage("Unknown card presented at the hackspace door.")

    def sendMessage(self, message):
        print message

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('172.31.24.101', 12345))
            s.send(message)
            s.close()
        except Exception, e:
            pass


listener = IrccatListener()
listener.listen()
