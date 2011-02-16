#!/usr/bin/python
import sys, os, time, re, socket, soundplayer, urllib2, random
from datetime import datetime

sys.path.append('../')
import DoorbotListener

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
  for f in os.listdir("./wavefiles/random"):
    randoms.append(f)

def playGreeting(id):
  random.seed()
  if id == '15FAA09E':
    soundplayer.main(["wavefiles/fixed/hackspacewelcome.wav","wavefiles/members/jonty.wav"])
  else:
    if id in waves.keys():
      if waves[id] == "broken.wav":
        soundplayer.main([waves[id]])
      else:
        soundplayer.main(["wavefiles/fixed/hackspacewelcome.wav","wavefiles/fixed/hackspacetestsubject.wav", "wavefiles/members/" + waves[id], "wavefiles/fixed/hackspacedoor.wav" ])
    else:
        soundplayer.main(["wavefiles/fixed/hackspacelonely.wav"])    

    if random.randint(0,5) == 4:
      r = random.randint(0,len(randoms) -1)
      soundplayer.main(["wavefiles/random/" + randoms[r] ]) 
  
def playDenied():
  soundplayer.main(["wavefiles/fixed/hackspacedenied.wav"])

def playDoorbell():
  soundplayer.main(["wavefiles/fixed/hackspacebingbong.wav"])


class GladosListener(DoorbotListener.DoorbotListener):

    def doorbell(self):
        print "Doorbell pushed"

        try:
            playDoorbell()
        except Exception, e:
            pass

    def doorOpened(self, serial, name):
        print "Door opened"

        try:
            playGreeting(serial)
        except Exception:
            pass

    def unknownCard(self, serial):
        print "Unknown card"

        try:
            playDenied()
        except Exception:
            pass


if __name__ == "__main__":
    loadGreetings()
    loadRandoms()

    listener = GladosListener()
    listener.listen()
