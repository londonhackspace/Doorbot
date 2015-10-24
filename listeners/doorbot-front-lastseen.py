#!/usr/bin/env python
import DoorbotListener, os, pickle, datetime, time
from DoorbotListener import config

class LastSeenListener(DoorbotListener.DoorbotListener):

    def doorOpened(self, serial, name):

        # To stop a race condition between us and the irc announce bot
        time.sleep(2)

        print "%s opened the front door, logging" % name

        lastseen = {}

        picklefile = config.get('lastseen', 'picklefile')
        
        if os.path.exists(picklefile):
            lastseen = pickle.load(open(picklefile))

        lastseen[name.lower()] = datetime.datetime.now()

        pickle.dump(lastseen, open(picklefile, 'wb'))


if __name__ == '__main__':
	listener = LastSeenListener()
	listener.listen(50002)
