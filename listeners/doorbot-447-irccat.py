#!/usr/bin/env python
d = __import__('doorbot-irccat')
d.PICKLEFILE = '/usr/share/irccat/.lastseen-447.pickle'
d.location = 'the door at the new space'
listener = d.IrccatListener()
listener.listen(50001)

