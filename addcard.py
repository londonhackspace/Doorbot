#!/usr/bin/env python

from urllib import urlencode
import urllib2, cookielib
from lxml import etree
from lxml.cssselect import CSSSelector
import getpass
import sys

BASE_URL = 'https://london.hackspace.org.uk/'
#BASE_URL = 'http://lhs.samsung/'

cookiejar = cookielib.CookieJar()
processor = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(processor)
urllib2.install_opener(opener)

def browse(url, params=None):
  if params is not None:
    params = urlencode(params)
  page = urllib2.urlopen(BASE_URL + url, params)
  return etree.HTML(page.read())

find_exception = CSSSelector('.exception')


if len(sys.argv) > 1:
  try:
    sys.path.append('RFIDIOt-0.1x') # use local copy for stability
    import RFIDIOtconfig

  except Exception, e:
    logging.critical('Error importing RFIDIOt: %s', e)
    sys.exit(1)

  card = RFIDIOtconfig.card
  print 'Checking for card...'

  while not card.select():
    # Yeah, we really should rewrite RFIDIOt
    if card.errorcode != card.PCSC_NO_CARD:
      raise Exception('Error %s selecting card' % card.errorcode)

  uid = card.uid

else:
  uid = raw_input('Card ID: ')

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
  print etree.tostring(exc[0], method="text", pretty_print=True)
  sys.exit(1)

loggedin_p = logged_in.xpath('//p[@id="loggedin"]')
if not loggedin_p:
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
  print etree.tostring(exc[0], method="text", pretty_print=True)
  sys.exit(1)

print "Card successfully added"
