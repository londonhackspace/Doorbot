from MQTTDoorbotListener import MQTTDoorbotListener
import os, random, subprocess
import logging
import sys

class GladosListener(MQTTDoorbotListener):

    def __init__(self):
        MQTTDoorbotListener.__init__(self)
        self.doors_of_interest = sys.argv[1].split(',')
        print ("Doors of interest: ")
        for door in self.doors_of_interest:
            print (".. " + door)
            
    def getcmd(self,sound):
        # Prerequisites for this command:
        # sudo apt-get install sox libsox-fmt-mp3
        return ['play', '-q', '--norm', str(sound), 'trim', '0', '00:17']

    def playSounds(self, sounds):
        print (sounds)
        for s in sounds:
            logging.info('Playing %s', s)
            subprocess.call(self.getcmd(s))
    
    def tts(self, string):
        if sys.platform == 'Darwin':
            os.system('echo "{0}" | say'.format(string))
        else:
            os.system('echo "{0}" | festival --tts'.format(string))

    def on_card(self, card_id, name, door, gladosfile):
        if door.getboolean('announce', True):
            for a_door in self.doors_of_interest:
                if (door['name'] == a_door):
                    print("%s presented card %s at door %s" % (name, card_id, door['name']))
                    if ( gladosfile ) :
                        g = os.getcwd()
                        os.chdir('glados-wavefiles/members')
                        self.playSounds([gladosfile])
                        os.chdir(g)
                    else:
                        # Let's try to text to speech it
                        self.tts(door['name'] + " sends greetings to %s" % (name))
        else:
            print("Will not announce stuff at %s" % (door['name'],))

    def on_unknown_card(self, card_id, door, user):
        print("unknown card %s presented at door %s" % (card_id, door['name']))
        self.playSounds(["glados-wavefiles/fixed/GlaDOS_intrusion_detected_Silent_alarm_.wav"])

    def on_start(self, door):
        print("%s started up" % (door['name'],))

    def on_alive(self, door):
        print("%s is alive" % (door['name'],))

    def on_bell(self, door):
        print("DING DONG! Door %s" % (door['name'],))
        for a_door in self.doors_of_interest:
                if (door['name'] == a_door):
                    self.playSounds(["glados-wavefiles/fixed/hackspacebingbong.wav"])

    def on_exit(self, door):
        print("Exit button pressed on %s" % (door['name'],))
        for a_door in self.doors_of_interest:
                if (door['name'] == a_door):
                    self.playSounds(["glados-wavefiles/fixed/you're_welcome.wav"])

    def on_denied(self, card_id, name, door):
        print("%s denied access with card %s at door %s" % (name, card_id, door['name']))
        for a_door in self.doors_of_interest:
                if (door['name'] == a_door):
                    self.playSounds(["glados-wavefiles/fixed/unexpected_item_in_bagging_area.mp3"])

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
dbl = GladosListener()

dbl.run()