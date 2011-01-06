#!/usr/bin/env python
import DoorbotListener, socket, random

class IrccatListener(DoorbotListener.DoorbotListener):

    def startup(self):
        self.sendMessage('This is doorbot')

        welcomes = [
            'This is doorbot and welcome to you who have come to doorbot',
            'Anything is possible with doorbot',
            'The infinite is possible with doorbot',
            'The unattainable is unknown with doorbot',
            'You can do anything with doorbot',
        ]
        welcomes += ['This is doorbot', 'Welcome to doorbot'] * 10
        self.sendMessage(random.choice(welcomes))

    def doorbell(self):
        self.sendMessage("BING BONG DOOR BELL! http://hackspace.org.uk:8003")

    def doorOpened(self, serial, name):
        self.sendMessage("%s opened the hackspace door." % name)

    def unknownCard(self, serial):
        self.sendMessage("Unknown card presented at the hackspace door.")

    def sendMessage(self, message):
        print message

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('172.31.24.101', 12345))
            s.send(message)
            s.close()
        except Exception, e:
            pass


listener = IrccatListener()
listener.listen()
