#!/usr/bin/python
import sys, os, time, re, socket, urllib2, random, subprocess
from datetime import datetime

sys.path.append('../')

wavefile = "wavetable.dat"
cardtable = "../../cardtable.dat"
output = "newwavetable.dat"


def loaddat(filename):
  f = open(filename)
  datdictionary = {}
  regex = re.compile("^([^\s]+)\s*((?:[^\s]| )+)?$")
  for n, line in enumerate(f):
    entry, h, comment = line.partition('#')
    if not entry.strip():
      continue
    match = regex.match(entry)
    if match:
      id, name = match.groups()
      datdictionary[id] = name
      #print id  + " " + name
    else:
      print 'Invalid entry at line %d' % n
  return datdictionary




if __name__ == "__main__":
    wave  = loaddat(wavefile)
    ids = loaddat(cardtable)
    for (k,v) in ids.iteritems():
      if k in wave: 
       print v + " " + wave[k] 
