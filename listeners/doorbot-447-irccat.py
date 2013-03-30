#!/usr/bin/env python
d = __import__('doorbot-irccat')
d.PICKLEFILE = '/usr/share/irccat/.lastseen-447.pickle'
d.PICKLEFILE = '.lastseen-447.pickle'
listener = d.IrccatListener()
listener.listen(50001)

