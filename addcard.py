#!/usr/bin/env python

from urllib import urlencode
import urllib2, cookielib
from lxml import etree
from lxml.cssselect import CSSSelector
import getpass
import sys
import os
import time
from RFUID import rfid

BASE_URL = 'https://london.hackspace.org.uk/'

cookiejar = cookielib.CookieJar()
processor = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(processor)
urllib2.install_opener(opener)

def browse(url, params=None):
    if params is not None:
        params = urlencode(params)
    page = urllib2.urlopen(BASE_URL + url, params)
    return etree.HTML(page.read())

find_exception = CSSSelector('.alert-danger')

if len(sys.argv) > 1:
    print 'Checking for card... (scan card on the RFID reader attached to this computer)'

    uid = None
    while uid is None:
        try:
            with rfid.Pcsc.reader() as reader:
                for tag in reader.pn532.scan():
                    uid = tag.uid.upper()
                    break
        except rfid.NoCardException:
            pass

        time.sleep(0.1)

    print 'Card UID is %s' % uid

else:
    uid = raw_input('Card UID: ')

email = raw_input('Email: ')
password = getpass.getpass('Password: ')
print

login = browse('login.php')
token = login.xpath('//input[@name="token"]')[0]

logged_in = browse('login.php', {
    'token': token.attrib['value'],
    'email': email,
    'password': password,
    'submit': 'Log In',
})

exc = find_exception(logged_in)
if exc:
    print 'Could not authenticate:'
    print
    print etree.tostring(exc[0], method="text", encoding='utf-8', pretty_print=True)
    sys.exit(1)

logout_a = logged_in.xpath('//a[@href="/logout.php"]')
if not logout_a:
    print 'Could not log in'
    sys.exit(1)

addcard = browse('/members/addcard.php')
token = addcard.xpath('//input[@name="token"]')[0]

card_added = browse('/members/addcard.php', {
    'token': token.attrib['value'],
    'uid': uid,
    'submit': 'Add',
})

exc = find_exception(card_added)
if exc:
    print 'Could not modify entry:'
    print
    print etree.tostring(exc[0], method="text", encoding='utf-8', pretty_print=True)
    sys.exit(1)

print "Card %s successfully added" % uid

