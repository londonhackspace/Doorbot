#!/usr/bin/env python
import DoorbotListener, os, pickle, datetime, time

PICKLEFILE = '/usr/share/irccat/.lastseen.pickle'

class LastSeenListener(DoorbotListener.DoorbotListener):

    def doorOpened(self, serial, name):

        # To stop a race condition between us and the irc announce bot
        time.sleep(2)

        print "%s opened the door, logging" % name

        lastseen = {}

        if os.path.exists(PICKLEFILE):
            lastseen = pickle.load(open(PICKLEFILE))

        lastseen[name.lower()] = datetime.datetime.now()

        pickle.dump(lastseen, open(PICKLEFILE, 'wb'))


listener = LastSeenListener()
listener.listen()
