#!/usr/bin/python
# Add a tag, based on:

#  isotype.py - determine ISO tag type
# 
#  Adam Laurie <adam@algroup.co.uk>
#  http://rfidiot.org/
# 
#  This code is copyright (c) Adam Laurie, 2006, All rights reserved.
#  For non-commercial use only, the following terms apply - for all other
#  uses, please contact the author:
#
#    This code is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#

import os
import re
import sys
# We're binding against the local copy for stability
sys.path.append('RFIDIOt-0.1x')

import RFIDIOtconfig


cardFile = 'cardtable.dat'



def addCard(id, name):
  
  file = open(cardFile, 'a')
  file.write('%s %s\n' % (id, name))
  file.close()

  os.system('scp cardtable.dat root@bell.lan:~/Doorbot/cardtable.dat')

def readCardTable():

  os.system('scp root@bell.lan:~/Doorbot/cardtable.dat cardtable.dat')

  # Two space separated fields, # for comments
  regex = re.compile("^([^#\n ]+) ([^#\n ]+)$")

  file = open(cardFile)
  cards = {}
  for line in file:
    if regex.match(line):
      matches = regex.findall(line)
      id, name = matches[0]
      cards[id] = name

  file.close()
  return cards


#name = sys.argv[1]
print 'Name to authorise:'
name = sys.stdin.readline()

card = RFIDIOtconfig.card

while True:
  card.select()
  id = card.uid

  if id == '':
    continue

  cards = readCardTable()

  if id in cards:
    print 'Card %s already authorised to %s\n' % (id, cards[id])

  else:
    addCard(id, name)
    print 'Card %s is now authorised to %s\n' % (id, name)

  os._exit(0)

os._exit(0)

