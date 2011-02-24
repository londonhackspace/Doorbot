#!/usr/bin/python
import sys, os, time, re, socket, urllib2, random, subprocess
from datetime import datetime

sys.path.append('../')
import DoorbotListener

wavefile = "wavetable.dat"

waves = {}
randoms = []
lastmodified = []


def playSoundsBackground( sounds):
  
   files  = [os.getcwd() + "/" + s  for s in sounds ]
   filesstring = " ".join(files)
   string =  "/usr/bin/mplayer "+ filesstring+ " < /dev/null &"
   #print string
   subprocess.Popen( string, shell=True) 

def playSounds(sounds):
  for sound in sounds:
    print "playing " + sound
    subprocess.call(["mplayer", sound])


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
   stat = os.stat (wavefile)
   print lastmodified
   if (not (stat.st_mtime in lastmodified)):
     print "loading greetings"   
     loadGreetings()
     del lastmodified[0]
     lastmodified.append(stat.st_mtime)
def loadRandoms ():
  for f in os.listdir("./wavefiles/random"):
    randoms.append(f)

def playGreeting(id):
  random.seed()
  print lastmodified
  welcome = re.compile("^welcome-")
  member = re.compile("^member-")
  mfolder = "wavefiles/members/"
  ffolder = "wavefiles/fixed/"
  rfolder = "wavefiles/random/"
  welcomesound = ffolder + "hackspacewelcome.wav"
  
  if id in waves:
    
    sounds = waves[id].split(' ')
    mainsound  = sounds[len(sounds)-1]
    memberfiles = [ mfolder + s  for s in sounds ]
 # More than one sound, play the first lot in the background   
    if len(sounds) > 1:
      length = len(sounds)
      playSoundsBackground (memberfiles[:length-1])
      membersound = memberfiles [length-1]
    else:
      membersound =  mfolder + waves [id]

    if member.match (mainsound):
      playSounds([welcomesound ,ffolder+ "hackspacetestsubject.wav", membersound , ffolder +"hackspacedoor.wav" ])

    elif welcome.match(mainsound):
      playSounds([ffolder + "hackspacewelcome.wav", membersound])
    else:
      playSounds([membersound])
  else:
      playSounds([ffolder + "hackspacelonely.wav"])    

  if random.randint(0,5) == 4:
    r = random.randint(0,len(randoms) -1)
    playSounds(["wavefiles/random/" + randoms[r] ]) 
  checkNewGreetings()
  
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
    lastmodified. append( os.stat(wavefile).st_mtime)
    print lastmodified
    listener = GladosListener()
    listener.listen()
