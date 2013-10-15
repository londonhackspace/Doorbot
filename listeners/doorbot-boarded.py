#!/usr/bin/env python
import DoorbotListener, urllib2

class BoardedListener(DoorbotListener.DoorbotListener):

    def doorbell(self):
        self.sendMessage("BING BONG DOOR BELL")

    def doorOpened(self, serial, name):
        self.sendMessage("%s opened the hackspace door" % name)

    def unknownCard(self, serial):
        self.sendMessage("Unknown card presented at the hackspace door")

    def sendMessage(self, message):
        text = "http://hamming.lan.london.hackspace.org.uk:8020/%s?restoreAfter=30" % urllib2.quote(message)
        print text

        try:
            urllib2.urlopen(text)
        except Exception, e:
            pass


listener = BoardedListener()
listener.listen()
