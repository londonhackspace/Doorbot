import os, pickle, datetime, time
from MQTTDoorbotListener import MQTTDoorbotListener

class LastSeenListener(MQTTDoorbotListener):

    def on_card(self, card_id, name, door, gladosfile):

        # To stop a race condition between us and the irc announce bot
        time.sleep(2)

        print("%s opened the door, logging" % name)

        lastseen = {}

        picklefile = self.config.get('lastseen', 'picklefile')

        if os.path.exists(picklefile):
            lastseen = pickle.load(open(picklefile,'rb'))

        lastseen[name.lower()] = datetime.datetime.now()

        pickle.dump(lastseen, open(picklefile, 'wb'))


if __name__ == '__main__':
    listener = LastSeenListener()
    listener.run()

