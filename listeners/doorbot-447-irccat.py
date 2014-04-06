#!/usr/bin/env python
d = __import__('doorbot-irccat')
d.PICKLEFILE = '/usr/share/irccat/.lastseen-447.pickle'
d.location = 'the hackspace back door'
d.doorbotname = 'back doorbot'
d.camurl = 'https://london.hackspace.org.uk/members/camera.php?id=12'
listener = d.IrccatListener()
listener.listen(50001)

