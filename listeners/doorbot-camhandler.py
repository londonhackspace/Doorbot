#!/usr/bin/env python
import DoorbotListener, os

class CamhandlerListener(DoorbotListener.DoorbotListener):

    def doorbell(self):
        os.system("grab-mjpeg.py localhost:8003 /var/www/doorbell.jpg")

    def unknownCard(self, serial):
        os.system("grab-mjpeg.py localhost:8003 /var/www/doorbell.jpg")


listener = CamhandlerListener()
listener.listen()
