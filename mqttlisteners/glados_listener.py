from MQTTDoorbotListener import MQTTDoorbotListener
import os, random, subprocess
import logging

class GladosListener(MQTTDoorbotListener):

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
        subprocess.call (['festival --tts'])

    def on_card(self, card_id, name, door, gladosfile):
        if door.getboolean('announce', True):
            print("%s presented card %s at door %s" % (name, card_id, door['name']))
            if ( gladosfile ) :
                g = os.getcwd()
                os.chdir('glados-wavefiles/members')
                self.playSounds([gladosfile])
                os.chdir(g)
            else:
                # Let's try to text to speech it
                self.tts("Greetings %s" % (name))

        else:
            print("Will not announce stuff at %s" % (door['name'],))

    def on_unknown_card(self, card_id, door):
        print("unknown card %s presented at door %s" % (card_id, door['name']))
        self.playSounds(["glados-wavefiles/fixed/GlaDOS_intrusion_detected_Silent_alarm_.wav"])

    def on_start(self, door):
        print("%s started up" % (door['name'],))

    def on_alive(self, door):
        print("%s is alive" % (door['name'],))

    def on_bell(self, door):
        print("DING DONG! Door %s" % (door['name'],))
        self.playSounds(["glados-wavefiles/fixed/hackspacebingbong.wav"])

    def on_exit(self, door):
        print("Exit button pressed on %s" % (door['name'],))
        self.playSounds(["glados-wavefiles/fixed/you're_welcome.wav"])

    def on_denied(self, card_id, name, door):
        print("%s denied access with card %s at door %s" % (name, card_id, door['name']))
        self.playSounds(["glados-wavefiles/fixed/unexpected_item_in_bagging_area.mp3"])

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
dbl = GladosListener()

dbl.run()