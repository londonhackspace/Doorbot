from MQTTDoorbotListener import MQTTDoorbotListener
import requests 
import time

class OLAListener(MQTTDoorbotListener):

    def set_colour(self, red,green,blue):
        server = self.config['ola']['server']
        url = "%s/set_dmx" % (server,)

        d = ""

        # 10 channels of lights
        for i in range(1,10):
            if i > 1:
                d = d + ","
            d = d + str(red)+","+str(green)+","+str(blue)

        data = { "u" : "1", "d" : d}

        requests.post(url = url, data = data)
        time.sleep(int(self.config['ola']['length']))

        d = ""
        for i in range(1,10):
            if i > 1:
                d = d + ","
            d = d + "0,0,0"

        data = { "u" : "1", "d" : d}

        requests.post(url = url, data = data)


    def on_card(self, card_id, name, door, gladosfile):
        if 'lights' in door:
            (r,g,b) = door['lights'].split(",")
            self.set_colour(r,g,b)
        else:
            print("door \"%s\" has no lights configured" % (door['name']))

    def on_unknown_card(self, card_id, door, user):
        if 'deny_colour' in self.config['ola']:
            (r,g,b) = self.config['ola']['bell_colour'].split(",")
            self.set_colour(r,g,b)

    def on_start(self, door):
        pass

    def on_alive(self, door):
        pass

    def on_bell(self, door):
        if 'bell_colour' in self.config['ola']:
            (r,g,b) = self.config['ola']['bell_colour'].split(",")
            self.set_colour(r,g,b)

    def on_exit(self, door):
        pass

    def on_denied(self, card_id, name, door):
        if 'deny_colour' in self.config['ola']:
            (r,g,b) = self.config['ola']['bell_colour'].split(",")
            self.set_colour(r,g,b)

olal = OLAListener()

olal.run()