#!/usr/bin/python
import os, random, subprocess
import logging
import json

import DoorbotListener

cardFile = '../carddb.json'

mTime = 0

greetings = {}
randoms = []

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
  global mTime
  global greetings

  try:
    currentMtime = os.path.getmtime(cardFile)
  except IOError, e:
    logging.critical('Cannot read card file: %s', e)
    raise

  if mTime != currentMtime:

    logging.debug('Loading card table, mtime %d', currentMtime)
    mTime = currentMtime
    greetings = {}

    file = open(cardFile)

    users = json.load(file)

    for user in users:
      if not user['gladosfile']:
        continue

      for card in user['cards']:
        card = card.encode('utf-8')
        greeting = user['gladosfile'].encode('utf-8')
        greetings[card] = greeting

    logging.info('Loaded %d cards', len(greetings))


def loadRandoms():
  for f in os.listdir("glados-wavefiles/random"):
    randoms.append(f)



def playGreeting(id):
  mfolder = "glados-wavefiles/members/"
  ffolder = "glados-wavefiles/fixed/"

  if id in greetings:

    sounds = greetings[id].split(' ')
    membersound = sounds[-1]
    membersound = os.path.basename(membersound)

    # FIXME: it seems wrong that these are played before the first one
    if len(sounds) > 1:
      # Play the first lot in the background
      soundfiles = [mfolder + s for s in sounds[:-1]]
      playSoundsBackground(soundfiles)

    if membersound.startswith('member-'):
      # Do the whole member spiel
      playSounds([
        ffolder + "hackspacewelcome.wav",
        ffolder + "hackspacetestsubject.wav",
        mfolder + membersound,
        ffolder + "hackspacedoor.wav",
      ])

    elif membersound.startswith('welcome-'):
      # Slightly abbreviated
      playSounds([
        ffolder + "hackspacewelcome.wav",
        mfolder + membersound,
      ])

    else:
      # Purely custom sound
      playSounds([
        mfolder + membersound,
      ])

  else:
      playSounds([ffolder + "hackspacelonely.wav"])    


  if random.randint(0,5) == 4:
    playSounds([
      "glados-wavefiles/random/" + random.choice(randoms),
    ])

 
 
def playDenied():
  playSounds(["glados-wavefiles/fixed/hackspacedenied.wav"])

def playDoorbell():
  playSounds(["glados-wavefiles/fixed/hackspacebingbong.wav"])


class GladosListener(DoorbotListener.DoorbotListener):

    def doorbell(self):
        print "Doorbell pushed"

        try:
            playDoorbell()
        except Exception, e:
            pass

    def doorOpened(self, serial, name):
        print "Door opened"

        loadGreetings()
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

    def trigger(self, serial):
        baseFolder = "glados-wavefiles/"
        print "Triggering " +  baseFolder + serial
        playSounds([baseFolder + serial])


if __name__ == "__main__":
    loadGreetings()
    loadRandoms()
    listener = GladosListener()
    listener.listen()

