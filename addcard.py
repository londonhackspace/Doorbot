#!/usr/bin/env python

from urllib import urlencode
import urllib2, cookielib
from lxml import etree
import getpass

BASE_URL = 'http://london.hackspace.org.uk/'
BASE_URL = 'http://lhs.samsung/'

cookiejar = cookielib.CookieJar()
processor = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(processor)
urllib2.install_opener(opener)

def browse(url, params=None):
  if params is not None:
    params = urlencode(params)
  page = urllib2.urlopen(BASE_URL + url, params)
  return etree.HTML(page.read())


uid = raw_input('Card ID: ')
email = raw_input('Email: ')
password = getpass.getpass('Password: ')


login = browse('login.php')
token = login.xpath('//input[@name="token"]')[0]

logged_in = browse('login.php', {
  'token': token.attrib['value'],
  'email': email,
  'password': password,
  'submit': 'Log In',
})

# TODO: make sure it worked

addcard = browse('/members/addcard.php')
token = addcard.xpath('//input[@name="token"]')[0]

card_added = browse('/members/addcard.php', {
  'token': token.attrib['value'],
  'uid': uid,
  'submit': 'Add',
})

# TODO: make sure it worked
