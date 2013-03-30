#!/usr/bin/env python
d = __import__('doorbot-lastseen')
d.PICKLEFILE = '/usr/share/irccat/.lastseen-447.pickle'
d.PICKLEFILE = '.lastseen-447.pickle'
listener = d.LastSeenListener()
listener.listen(50001)

