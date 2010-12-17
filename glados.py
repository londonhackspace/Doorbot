#!/usr/bin/python
import sys, os, time, re, socket, soundplayer, urllib2, random
from datetime import datetime

wavefile = "wavetable.dat"

waves = {}
randoms = []


def loadGreetings():
  f = open(wavefile)
  regex = re.compile("^([^\s]+)\s*((?:[^\s]| )+)?$")
  for n, line in enumerate(f):
    entry, h, comment = line.partition('#')
    if not entry.strip():
      continue
    match = regex.match(entry)
    if match:
      id, name = match.groups()
      waves[id] = name
    else:
      print 'Invalid entry at line %d' % n

def loadRandoms ():
  for f in os.listdir("./glados/random"):
    randoms.append(f)

def playGreeting(id):
  random.seed()
  if id == '15FAA09E':
    soundplayer.main(["glados/fixed/hackspacewelcome.wav","glados/members/jonty.wav"])
  else:
    if id in waves.keys():
      if waves[id] == "broken.wav":
        soundplayer.main([waves[id]])
      else:
        soundplayer.main(["glados/fixed/hackspacewelcome.wav","glados/fixed/hackspacetestsubject.wav", "glados/members/" + waves[id], "glados/fixed/hackspacedoor.wav" ])
    if random.randint(0,5) == 4:
      r = random.randint(0,len(randoms) -1)
      soundplayer.main(["glados/random/" + randoms[r] ]) 
  
def playDenied():
  soundplayer.main(["glados/fixed/hackspacedenied.wav"])

def playDoorbell():
  soundplayer.main(["glados/fixed/hackspacebingbong.wav"])

if __name__ == "__main__":
  random.seed()
  loadGreetings()
  loadRandoms()
  playGreeting("37220641")
