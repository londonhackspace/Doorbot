#!/usr/bin/env python
d = __import__('doorbot-irccat')
d.location = 'the hackspace front door'
d.welcomes = ['This is front doorbot']
listener = d.IrccatListener()
listener.listen(50002)

