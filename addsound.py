#!/usr/bin/env python

from urllib import urlencode
import urllib2, cookielib
from lxml import etree
from lxml.cssselect import CSSSelector
import getpass
import sys
import os
import time

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
  print 'Could not authenticate'
  print
  print etree.tostring(exc[0], method="text", pretty_print=True)
  sys.exit(1)

loggedin_p = logged_in.xpath('//p[@id="loggedin"]')
if not loggedin_p:
  print 'Could not log in'
  sys.exit(1)

# add sound
print "Adding a sound file to the entry system"
print ""
print "In a moment, I will be opening nautilus to the upload directory, where you must copy your sound file to;"
print ""
os.system("nautilus ./upload")
os.system("rm -Rf ./upload/*")

raw_input("When the file has finished transfering to lovelace, Press enter to continue")
upload_path = "./upload"
# haven't written code to detect for .wav specifically
if len(os.listdir(upload_path)) == 1:
  print "Detected one file in the upload directory, this is a good thing."
else:
  print "sorry, but you have %s files in the upload directory and we only need 1.. please check this and/or ask for help." % len(os.listdir(path))
  sys.exit(1)

updatesound = browse('/members/cards.php')
newtoken = updatesound.xpath('//input[@name="token"]')[0]
nickname = updatesound.xpath('//input[@name="nickname"]')[0]

newfilename = "[H]" + str(time.time()) + ".wav";

sound_updated = browse('/members/cards.php', {
  'token': newtoken.attrib['value'],
  'gladosfile': newfilename,
  'submit': 'Save',
  'update_details': '',
  'nickname': nickname.attrib['value'],
})
os.system("curl -F \"upload=@`ls ./upload/*`;filename=" + newfilename + ";name=upload;\" http://hack.rs/~glados/glados.php")

print ""
print "Thank you '%s' for updating your information" % nickname.attrib['value']
exc = find_exception(sound_updated)
if exc:
  print 'Could not modify entry sound'
  print
  print etree.tostring(exc[0], method="text", pretty_print=True)
  sys.exit(1)

