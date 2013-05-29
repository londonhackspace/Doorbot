#!/usr/bin/env python
d = __import__('doorbot-lastseen')
d.PICKLEFILE = '/usr/share/irccat/.lastseen-24.pickle'
listener = d.LastSeenListener()
listener.listen(50001)

