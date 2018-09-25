#!/usr/bin/env python
import DoorbotListener, urllib2

class BoardedListener(DoorbotListener.DoorbotListener):

    def doorbell(self):
        self.sendMessage("BING BONG DOOR BELL")

    def doorOpened(self, serial, name):
        self.sendMessage("%s opened the hackspace 1st floor door" % name)
	self.sendMessage_bwmeter("Welcome %s" % name)

    def unknownCard(self, serial):
        self.sendMessage("Unknown card presented at the hackspace 1st floor door")

    def sendMessage(self, message):
        text = "http://wilson.lan.london.hackspace.org.uk:8020/%s?restoreAfter=30" % urllib2.quote(message)
        print text

        try:
            urllib2.urlopen(text)
        except Exception, e:
            pass

    def sendMessage_bwmeter(self, message):
	text = "http://10.0.70.17/v/c"
        try:
            urllib2.urlopen(text)
        except Exception, e:
            pass
	text = "http://10.0.70.17/v/w?%s" % urllib2.quote(message)
        try:
            urllib2.urlopen(text)
        except Exception, e:
            pass


listener = BoardedListener()
listener.listen(50003)
