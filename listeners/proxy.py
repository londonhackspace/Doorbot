#!/usr/bin/env python
import socket

def listen():
    s = socket.socket()
    s.bind(('', 50001))
    s.listen(1)

    while True:
        try:
            conn, addr = s.accept()
            payload = conn.recv(1024)
            conn.close()
            broadcast(payload)

        except Exception, e:
            print 'Error: %s' % e


def broadcast(data):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 0))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print 'broadcasting %s' % data
    s.sendto(data, ('<broadcast>', 50001))

if __name__ == '__main__':
    listen()
