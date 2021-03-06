from MQTTDoorbotListener import MQTTDoorbotListener

class TestListener(MQTTDoorbotListener):

    def on_card(self, card_id, name, door, gladosfile):
        if door.getboolean('announce', True):
            print("%s presented card %s at door %s" % (name, card_id, door['name']))
        else:
            print("Will not announce stuff at %s" % (door['name'],))

    def on_unknown_card(self, card_id, door, user):
        print("unknown card %s (user %s) presented at door %s" % (card_id, user, door['name']))

    def on_start(self, door):
        print("%s started up" % (door['name'],))

    def on_alive(self, door):
        print("%s is alive" % (door['name'],))

    def on_bell(self, door):
        print("DING DONG! Door %s" % (door['name'],))

    def on_exit(self, door, doorbellack):
        print("Exit button pressed on %s" % (door['name'],))
        if (doorbellack):
            print("..in response to a recent doorbell")

    def on_denied(self, card_id, name, door):
        print("%s denied access with card %s at door %s" % (name, card_id, door['name']))

dbl = TestListener()

dbl.run()