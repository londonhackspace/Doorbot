#!/usr/bin/env python
import DoorbotListener, time, urllib2

class LightedListener(DoorbotListener.DoorbotListener):

    def doorbell(self):
        print "Doorbell pushed"

        self.flashLights('0,255,0', 1)
        time.sleep(2)
        self.flashLights('0,255,0', 1)
        time.sleep(2)
        self.flashLights('0,255,0', 1)

    def doorOpened(self, serial, name):
        print "Door opened"

        self.flashLights('0,0,255', 10)

    def unknownCard(self, serial):
        print "Unknown card"

        self.flashLights('255,0,0', 1)
        time.sleep(2)
        self.flashLights('255,0,0', 1)

    def flashLights(self, colour, time):
        try:
            urllib2.urlopen("http://172.31.24.5:8010/_/%s?restoreAfter=%s" % (colour, time))
        except Exception, e:
            pass
        

listener = LightedListener()
listener.listen()
