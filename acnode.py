#!/usr/bin/env python
import re
import sys, os
import logging
import time
import json
import socket
import urlparse
import BaseHTTPServer
import ConfigParser

SERVICE = 'acnode'

config = ConfigParser.ConfigParser()
configs = [
    '%(service)s.conf',
    '/etc/%(service)s.conf',
    '%(scriptdir)s/%(service)s.conf'
]
if not sys.path[0]:
    sys.path[0] = '.'
config.read(map(lambda x: x % {'scriptdir': sys.path[0], 'service': SERVICE}, configs))

PORT = config.getint(SERVICE, 'tcpport')


logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
logging.info('Starting %s' % SERVICE)

cardFile = 'carddb.json'
mTime = 0
cards = {}
perms = {}
nodes = {}

class Node(object):
    def __init__(self, nodeid, perm):
        self.nodeid = nodeid
        self.perm = perm
        self.perms = {}
        self.cards = []
        self.status = 1
        self.tooluse = 0
        self.case = 0
        self.newperms = {}

    def updatePerms(self, perms):
        self.perms = {}
        for card, userperms in perms.items():
            if self.perm in userperms:
                self.perms[card] = 1

        self.perms.update(self.newperms)

    def checkCard(self, uid):
        reloadCardTable()
        return self.perms.get(uid, 0)

    def getCard(self, uid=None):
        if uid is None:
            reloadCardTable()
            self.cards = sorted(self.perms.keys())
            index = 0
        else:
            # KeyError if not initialised, ValueError if unknown card
            index = self.cards.index(uid) + 1
        
        try:
            return self.cards[index]
        except IndexError:
            return None

    def addCard(self, uid):
        self.newperms[uid] = 1
        self.perms.update(self.newperms)

for nodeid, perm in config.items('nodeperm'):
    nodes[nodeid] = Node(nodeid, perm)


def reloadCardTable():
    global mTime
    global cards

    try:
        currentMtime = os.path.getmtime(cardFile)
    except IOError, e:
        logging.critical('Cannot read card file: %s', e)
        raise

    if mTime != currentMtime:

        logging.debug('Loading card table, mtime %d', currentMtime)
        mTime = currentMtime
        cards = {}

        file = open(cardFile)

        users = json.load(file)

        for user in users:
            for card in user['cards']:
                card = card.encode('utf-8')
                nick = user['nick'].encode('utf-8')
                cards[card] = nick
                perms[card] = user['perms']

        for node in nodes.values():
            node.updatePerms(perms)

        logging.info('Loaded %d cards', len(cards))


def broadcast(event, card, name):

    try:
        logging.debug('Broadcasting %s to network', event)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        data = "%s\n%s\n%s" % (event, card, name)
        s.sendto(data, ('<broadcast>', 50000))

    except Exception, e:
        logging.warn('Exception during broadcast: %s', e)


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    # Disable logging DNS lookups
    def address_string(self):
        return str(self.client_address[0])

    def route(self, dispatches):
        start = time.time()

        self.url = urlparse.urlparse(self.path)
        self.params = urlparse.parse_qs(self.url.query)

        for pattern, dispatch in dispatches:
            m = re.match(pattern, self.path)
            if m:
                try:
                    dispatch(*m.groups())

                except Exception, e:
                    self.send_response(500)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()

                    self.wfile.write('%s\n' % e)

                    logging.debug(repr(e))

                break

        else:
            self.send_error(500)

        end = time.time()
        logging.debug('Time taken: %0.3f ms' % ((end - start) * 1000))

    def do_GET(self):

        def html_ok():
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

        def html_unauth():
            self.send_response(401)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

        def do_index():
            html_ok()

            self.wfile.write('Path: %s\n' % repr(self.path))
            self.wfile.write('Params: %s\n' % repr(self.params))
            self.wfile.write('http://wiki.london.hackspace.org.uk/view/Project:Tool_Access_Control\n')

        def do_card(nodeid, uid):
            try:
                node = nodes[nodeid]
            except KeyError, e:
                access = 0
            else:
                access = node.checkCard(uid)

            html_ok()
            self.wfile.write(access)

        def do_sync(nodeid, uid=None):
            
            try:
                node = nodes[nodeid]

            except KeyError, e:
                raise ValueError('Unknown node %s' % nodeid)

            card = node.getCard(uid)

            if card:
                html_ok()
                self.wfile.write(card)
            else:
                html_ok()
                self.wfile.write('END')

        def do_status(nodeid):
            html_ok()
            self.wfile.write(nodes[nodeid].status)


        self.route([
            ('^/(\d+)/card(?:/?|/([A-Z0-9]+)/?)$', do_card),
            ('^/(\d+)/sync(?:/?|/([A-Z0-9]+)/?)$', do_sync),
            ('^/(\d+)/status/?$', do_status),
            ('^/.*$', do_index),
        ])

    def do_POST(self):

        def html_ok():
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

        def html_notallowed():
            self.send_response(405)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

        def html_forbidden():
            self.send_response(403)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

        def do_index():
            html_notallowed()

            self.wfile.write('Path: %s\n' % repr(self.path))
            self.wfile.write('Params: %s\n' % repr(self.params))
            self.wfile.write('http://wiki.london.hackspace.org.uk/view/Project:Tool_Access_Control\n')

        def do_card(nodeid):
            node = nodes[nodeid]

            length = int(self.headers['Content-length'])
            uid = self.rfile.read(length)
            node.addCard(uid)

            html_ok()
            self.wfile.write('OK')


        self.route([
            ('^/(\d+)/card/?$', do_card),
            ('^/.*$', do_index),
        ])


    def do_PUT(self):

        def html_ok():
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

        def html_bad():
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

        def html_notallowed():
            self.send_response(405)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

        def do_index():
            html_notallowed()

            self.wfile.write('Path: %s\n' % repr(self.path))
            self.wfile.write('Params: %s\n' % repr(self.params))
            self.wfile.write('http://wiki.london.hackspace.org.uk/view/Project:Tool_Access_Control\n')

        def do_card(nodeid, uid):
            node = nodes[nodeid]
            node.newperms[uid] = 1

            html_ok()
            self.wfile.write('OK')

        def do_status(nodeid):
            node = nodes[nodeid]
            length = int(self.headers['Content-length'])
            status = self.rfile.read(length)
            if status.strip() in ('1', '0'):
                node.status = int(status)
                html_ok()
                self.wfile.write('OK')
            else:
                html_bad()
                self.wfile.write('Invalid status\n')

        def do_tooluse(nodeid):
            node = nodes[nodeid]
            length = int(self.headers['Content-length'])
            tooluse = self.rfile.read(length)
            if tooluse.strip() in ('1', '0'):
                node.tooluse = int(tooluse)
                html_ok()
                self.wfile.write('OK')
            else:
                html_bad()
                self.wfile.write('Invalid tooluse\n')

        def do_case(nodeid):
            node = nodes[nodeid]
            length = int(self.headers['Content-length'])
            case = self.rfile.read(length)
            if case.strip() in ('1', '0'):
                node.case = int(case)
                html_ok()
                self.wfile.write('OK')
            else:
                html_bad()
                self.wfile.write('Invalid case\n')


        self.route([
            ('^/(\d+)/status/?$', do_status),
            ('^/(\d+)/tooluse/?$', do_tooluse),
            ('^/(\d+)/case/?$', do_case),
            ('^/.*$', do_index),
        ])



reloadCardTable()
httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
logging.info('Started on port %s', PORT)
httpd.serve_forever()

