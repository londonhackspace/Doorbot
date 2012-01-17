#!/usr/bin/env python
import DoorbotListener, pynotify

class NotifyListener(DoorbotListener.DoorbotListener):

    def doorbell(self):
        self.sendMessage(
            "BING BONG!",
            "Someone pressed the hackspace doorbell."
        )

    def doorOpened(self, serial, name):
        self.sendMessage(
            "Door opened",
            "%s opened the hackspace door." % name
        )

    def unknownCard(self, serial):
        self.sendMessage(
            "ALERT",
            "An unknown RFID card was used on the hackspace door."
        )

    def sendMessage(self, title, message):
        pynotify.Notification(title, message).show()


listener = NotifyListener()
listener.listen()
