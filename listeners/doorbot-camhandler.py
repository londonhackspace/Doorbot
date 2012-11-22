#!/usr/bin/env python
import DoorbotListener, os, time

class CamhandlerListener(DoorbotListener.DoorbotListener):

    def doorbell(self):
        print 'Doorbell rung: grabbing images'
        os.system("/usr/local/bin/grab-mjpeg.py localhost:8003 /var/www/doorbell.jpg")
        for n in range(5):
            print '%s/5' % (n+1)
            self.grabimage(n)

    def grabimage(self, n):
        os.system("/usr/local/bin/grab-mjpeg.py localhost:8003 /var/www/doorbell/%s.jpg" % n)
        time.sleep(1)

    def unknownCard(self, serial):
        print 'Unknown card: grabbing image'
        os.system("/usr/local/bin/grab-mjpeg.py localhost:8003 /var/www/doorbell.jpg")


listener = CamhandlerListener()
listener.listen()
