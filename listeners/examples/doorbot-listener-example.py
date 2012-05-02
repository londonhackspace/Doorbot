#!/usr/bin/env python
import socket, random, sys
sys.path.append('../')
import DoorbotListener

class ExampleListener(DoorbotListener.DoorbotListener):

    def startup(self):
        print "Doorbot started."

    def doorbell(self):
        print "Doorbell pressed."

    def doorOpened(self, serial, name):
        print "Door opened by %s, card serial %s." % (name, serial)

    def unknownCard(self, serial):
        print "Unknown card %s presented at the door." % (serial)

    def trigger(self, filename):
        print "Audio file [%s] triggered." % (filename)

listener = ExampleListener()
listener.listen()
