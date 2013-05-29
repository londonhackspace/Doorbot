#!/usr/bin/env python
d = __import__('doorbot-irccat')
d.PICKLEFILE = '/usr/share/irccat/.lastseen-24.pickle'
d.location = 'the door at the old space'
d.welcomes = ['This is doorbot at the old space']
listener = d.IrccatListener()
listener.listen(50001)

