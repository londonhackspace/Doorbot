import logging
import socket

__all__ = ['Broadcast', 'Proxy']

class Broadcast(object):
    def __init__(self, port=50000):
        self.port = int(port)

    def send(self, event, card, name):
        try:
            logging.debug('Broadcasting %s to network', event)

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            data = "%s\n%s\n%s" % (event, card, name)
            s.sendto(data, ('<broadcast>', self.port))

        except Exception, e:
            logging.warn('Exception during broadcast: %s', e)


class Proxy(object):
    def __init__(self, host, port=50000):
        self.host = host
        self.port = int(port)

    def send(self, event, card, name):
        try:
            logging.debug('Sending %s to proxy', event)

            s = socket.socket()
            s.settimeout(5)
            s.connect((self.host, self.port))

            data = "%s\n%s\n%s" % (event, card, name)
            s.send(data)
            s.close()

        except Exception, e:
            logging.warn('Exception during send: %s', e)

