#!/usr/bin/env python
d = __import__('doorbot-irccat')
d.location = 'the hackspace front door'
d.doorbotname = 'front doorbot'
d.camurl = 'https://london.hackspace.org.uk/members/camera.php?id=14'
listener = d.IrccatListener()
listener.listen(50002)

