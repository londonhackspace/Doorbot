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
DOCSPAGE = config.get(SERVICE, 'docspage')


logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
logging.info('Starting %s' % SERVICE)

cardFile = 'carddb.json'
mTime = 0
cards = {}
perms = {}
nodes = {}

class NotFoundError(Exception):
  pass

class NoLengthError(Exception):
  pass

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
            if '%s-maintainer' % self.perm in userperms:
                self.perms[card] = 2

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
            # ValueError if unknown card
            index = self.cards.index(uid) + 1
        
        try:
            return self.cards[index]
        except IndexError, e:
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
        logging.critical('Cannot read card file: %s', repr(e))
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
        logging.warn('Exception during broadcast: %s', repr(e))


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    error_content_type = 'text/plain'

    # Disable logging DNS lookups
    def address_string(self):
        return str(self.client_address[0])

    def route(self, dispatches):
        start = time.time()

        self.url = urlparse.urlparse(self.path)
        self.params = urlparse.parse_qs(self.url.query)

        if 'Accept' in self.headers:
            # FIXME: parse properly
            for t in self.headers['Accept'].split(','):
                t, _, p = t.partition(';')
                if 'text/plain' in t or '*/*' in t:
                    break
            else:
                html_notacceptable()
                self.wfile.write('Sorted types: text/plain\n')
                return

        for pattern, dispatch in dispatches:
            m = re.match(pattern, self.path)
            if m:
                try:
                    dispatch(*m.groups())

                except NotFoundError, e:
                    self.text_notfound()
                    self.wfile.write('%s\n' % repr(e))

                except NoLengthError, e:
                    self.text_nolength()
                    self.wfile.write('%s\n' % repr(e))

                except ValueError, e:
                    self.text_bad()
                    self.wfile.write('%s\n' % repr(e))

                except Exception, e:
                    self.text_error()
                    self.wfile.write('%s\n' % repr(e))

                    logging.debug(repr(e))

                break

        else:
            self.text_bad()

        end = time.time()
        logging.debug('Time taken: %0.3f ms' % ((end - start) * 1000))

    def text_response(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def text_ok(self):
        self.text_response(200)

    def text_added(self):
        self.text_response(201)

    def text_nocontent(self):
        self.text_response(204)

    def text_partial(self):
        self.text_response(206)

    def text_bad(self):
        self.text_response(400)

    def text_unauth(self):
        self.text_response(401)

    def text_forbidden(self):
        self.text_response(403)

    def text_notfound(self):
        self.text_response(404)

    def text_badmethod(self, valid_methods):
        self.send_response(405)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Accept', ','.join(valid_methods))
        self.end_headers()

    def text_notacceptable(self):
        self.text_response(406)

    def text_conflict(self):
        self.text_response(409)

    def text_nolength(self):
        self.text_response(411)

    def text_error(self):
        self.send_error(500)

    def text_notimplemented(self):
        self.send_error(501)


    def urlnode(self, nodeid):
        try:
            return nodes[nodeid]
        except KeyError, e:
            raise NotFoundError(nodeid)

    def content(self):
        try:
            length = self.headers['Content-length']
            length = int(length)
            return self.rfile.read(length)
        except Exception, e:
            raise NoLengthException(str(e))

    def do_GET(self):

        def do_index():
            self.text_ok()

            self.wfile.write('Path: %s\n' % repr(self.path))
            self.wfile.write('Params: %s\n' % repr(self.params))
            self.wfile.write('%s\n' % DOCSPAGE)

        def do_card(nodeid, uid):
            node = self.urlnode(nodeid)
            access = node.checkCard(uid)

            if access:
                self.text_ok()
                self.wfile.write(access)

            else:
                self.text_notfound()
                self.wfile.write(access)

        def do_sync(nodeid, uid=None):
            node = self.urlnode(nodeid)
            card = node.getCard(uid)

            if card:
                self.text_partial()
                self.wfile.write(card)

            else:
                self.text_nocontent()

        def do_status(nodeid):
            node = self.urlnode(nodeid)

            self.text_ok()
            self.wfile.write(node.status)


        self.route([
            ('^/(\d+)/card(?:/?|/([A-Z0-9]+)/?)$', do_card),
            ('^/(\d+)/sync(?:/?|/([A-Z0-9]+)/?)$', do_sync),
            ('^/(\d+)/status/?$', do_status),
            ('^/$', do_index),
            ('', self.text_notfound),
        ])

    def do_POST(self):

        def do_index():
            self.text_badmethod(['GET'])

            self.wfile.write('Path: %s\n' % repr(self.path))
            self.wfile.write('Params: %s\n' % repr(self.params))
            self.wfile.write('%s\n' % DOCSPAGE)

        def do_card(nodeid):
            node = self.urlnode(nodeid)
            uids = self.content()
            m = re.match('^([A-Z0-9]+),([A-Z0-9]+)$', uids)
            if not m:
                self.text_bad()
                return

            maintainer_uid, user_uid = m.groups()
            maintainer_access = node.checkCard(maintainer_uid)

            if maintainer_access < 2:
                self.text_forbidden()
                return

            user_access = node.checkCard(user_uid)
            if user_access: # no change
                self.text_ok()
                self.wfile.write('OK (was %s)' % user_access)

            else:
                node.addCard(user_uid)

                self.text_added()
                self.wfile.write('OK')


        self.route([
            ('^/(\d+)/card/?$', do_card),
            ('^/$', do_index),
            ('', self.text_notfound),
        ])


    def do_PUT(self):

        def do_index():
            self.text_badmethod(['GET'])

            self.wfile.write('Path: %s\n' % repr(self.path))
            self.wfile.write('Params: %s\n' % repr(self.params))
            self.wfile.write('%s\n' % DOCSPAGE)

        def do_card(nodeid, uid):
            node = self.urlnode(nodeid)
            node.newperms[uid] = 1

            self.text_ok()
            self.wfile.write('OK')

        def do_status(nodeid):
            node = self.urlnode(nodeid)
            status = self.content()

            if status.strip() in ('1', '0'):
                node.status = int(status)
                self.text_ok()
                self.wfile.write('OK')

            else:
                self.text_bad()
                self.wfile.write('Invalid status\n')

        def do_tooluse(nodeid):
            node = self.urlnode(nodeid)
            args = self.content()
            m = re.match('^([0-9]+),([A-Z0-9]+)$', args)
            if not m:
                self.text_bad()
                self.wfile.write('Invalid arguments\n')
                return

            tooluse, uid = m.groups()
            access = node.checkCard(uid)

            if not access:
                self.text_forbidden()
                return

            if tooluse.strip() in ('1', '0'):
                node.tooluse = int(tooluse)
                self.text_ok()
                self.wfile.write('OK')

            else:
                self.text_bad()
                self.wfile.write('Invalid tooluse\n')

        def do_case(nodeid):
            node = self.urlnode(nodeid)
            case = self.content()

            if case.strip() in ('1', '0'):
                node.case = int(case)
                self.text_ok()
                self.wfile.write('OK')

            else:
                self.text_bad()
                self.wfile.write('Invalid case\n')


        self.route([
            ('^/(\d+)/status/?$', do_status),
            ('^/(\d+)/tooluse/?$', do_tooluse),
            ('^/(\d+)/case/?$', do_case),
            ('^/$', do_index),
            ('', self.text_notfound),
        ])



reloadCardTable()

httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
logging.info('Started on port %s', PORT)
httpd.serve_forever()

