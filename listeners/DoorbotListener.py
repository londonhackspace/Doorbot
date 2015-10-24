import select, socket, sys
from ConfigParser import ConfigParser
from carddb import CardDB

class DoorbotListener():
    def __init__(self):
        self.carddb = CardDB()

    def listen(self, port=50000):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#        s.bind(('<broadcast>', port))
        s.bind(('', port))
        s.setblocking(0)

        while True:

            try:

                result = select.select([s],[],[])
                payload = result[0][0].recv(1024)
                (event, serial, _) = payload.split("\n")

                if event == 'RFID':
                    name = self.carddb.nickForCard(serial)
                    if name:
                        self.doorOpened(serial, name)
                    else:
                        self.unknownCard(serial)

                elif (event == 'BELL'):
                    self.doorbell()

                elif (event == 'START'):
                    self.startup()

                #for triggering sounds, the "serial" field is just the name of a .wav file
                elif (event == "TRIGGER"):
                    self.trigger(serial)

            except Exception, e:
                print 'Exception in handler %s' % repr(e)


    def doorOpened(self, serial, name):
        pass

    def unknownCard(self, serial):
        pass

    def doorbell(self):
        pass

    def startup(self):
        pass

    def trigger(self, serial):
        pass



class Doorbot(object):
    def __init__(self, params):
        self.__dict__ = params

config = ConfigParser()
config.read([
    'doorbot-listener.conf',
    sys.path[0] + '/doorbot-listener.conf',
    '/etc/doorbot-listener.conf',
])

doorbots = {}
def get_doorbot(doorbotname):
    try:
        doorbot = doorbots[doorbotname]
    except KeyError:
        # will raise a NoSectionError if invalid
        params = dict(config.items(doorbotname))
        doorbot = Doorbot(params)

        doorbots[doorbotname] = doorbot

    return doorbot

