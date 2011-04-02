#!/usr/bin/python
import sys, os, time, re, socket, urllib2, random, subprocess
from datetime import datetime

sys.path.append('../')
import DoorbotListener

wavefile = "wavetable.dat"

waves = {}
randoms = []
lastmodified = []

random.seed()


def getcmd(sound):
  if sound.endswith('mp3'):
    return 'mpg123 %s' % sound
  else:
    return 'aoss bplay %s '% sound
 
def playSoundsBackground( sounds):
  cmds = [getcmd(s) for s in sounds]

  # & is for Windows support
  cmdstring = '; '.join(cmds) + ' &'
  print 'Playing %s' % cmdstring

  subprocess.Popen(cmdstring, shell=True) 

def playSounds(sounds):
  cmds = [getcmd(s) for s in sounds]

  cmdstring = '; '.join(cmds)
  print 'Playing %s' % cmdstring

  proc = subprocess.Popen(cmdstring, shell=True)
  proc.wait()



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
      #print id  + " " + name
    else:
      print 'Invalid entry at line %d' % n

def checkNewGreetings():
  try:
    stat = os.stat(wavefile)
    if stat.st_mtime != lastmodified:
      print "Loading new greetings"
      loadGreetings()
      lastmodified = stat.st_mtime

  except Exception, e:
    print 'Unable to check for new greetings'

def loadRandoms ():
  for f in os.listdir("wavefiles/random"):
    randoms.append(f)



def playGreeting(id):
  mfolder = "wavefiles/members/"
  ffolder = "wavefiles/fixed/"
  welcomesound = ffolder + "hackspacewelcome.wav"
  
  if id in waves:
    
    sounds = waves[id].split(' ')
    memberfiles = [ mfolder + s for s in sounds ]

    if len(sounds) > 1:
      # Play the first lot in the background   
      length = len(sounds)
      playSoundsBackgrounda(memberfiles[:-1])

    membersound = memberfiles[-1]

    if membersound.startswith('member-'):
      # Do the whole member spiel
      playSounds([
        welcomesound,
        ffolder + "hackspacetestsubject.wav",
        membersound,
        ffolder + "hackspacedoor.wav",
      ])

    elif membersound.startswith('welcome-'):
      # Slightly abbreviated
      playSounds([
        welcomesound,
        membersound,
      ])

    else:
      # Purely custom sound
      playSounds([
        membersound,
      ])

  else:
      playSounds([ffolder + "hackspacelonely.wav"])    


  if random.randint(0,5) == 4:
    playSounds([
      "wavefiles/random/" + random.choice(randoms),
    ])

 
 
def playDenied():
  playSounds(["wavefiles/fixed/hackspacedenied.wav"])

def playDoorbell():
  playSounds(["wavefiles/fixed/hackspacebingbong.wav"])


class GladosListener(DoorbotListener.DoorbotListener):

    def doorbell(self):
        print "Doorbell pushed"

        try:
            playDoorbell()
        except Exception, e:
            pass

    def doorOpened(self, serial, name):
        print "Door opened"

        checkNewGreetings()
        try:
            playGreeting(serial)
        except Exception, e:
           print e
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
    lastmodified = os.stat(wavefile).st_mtime
    print lastmodified
    listener = GladosListener()
    listener.listen()

