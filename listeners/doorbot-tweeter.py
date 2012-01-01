#!/usr/bin/env python
import DoorbotListener, twitter

class TweeterListener(DoorbotListener.DoorbotListener):

    def doorbell(self):
        # Tweet the snapshot and the event.
        api = twitter.Api(consumer_key='consumer_key',consumer_secret='consumer_secret', access_token_key='access_token', access_token_secret='access_token_secret')
        api.postUpdate("Bing bong, someone rang the doorbell! http://hack.rs/doorcam.jpg")
        
    def unknownCard(self, serial):
        # TODO: Me. Do I want to tweet when some evildoer tries to sneak in?

listener = TweeterListener()
listener.listen()
