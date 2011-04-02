#!/usr/bin/env python
import DoorbotListener, os, pickle, datetime

PICKLEFILE = '/usr/share/irccat/.lastseen.pickle'

class LastSeenListener(DoorbotListener.DoorbotListener):

    def doorOpened(self, serial, name):

        print "%s opened the door, logging" % name

        lastseen = {}

        if os.path.exists(PICKLEFILE):
            lastseen = pickle.load(open(PICKLEFILE))

        lastseen[name.lower()] = datetime.datetime.now()

        pickle.dump(lastseen, open(PICKLEFILE, 'wb'))


listener = LastSeenListener()
listener.listen()
