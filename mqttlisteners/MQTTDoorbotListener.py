from configparser import ConfigParser
from ACServerLookup import ACServerLookup
import paho.mqtt.client as mqtt
import sys
import json

def on_mqtt_connect(client, userdata, flags, rc):
    print("Connected to MQTT server")
    userdata._mqtt_connect(client, flags, rc)

def on_mqtt_message(client, userdata, msg):
    try:
        userdata._mqtt_message(client, msg)
    except Exception as e:
        print("Error handing message \"%s\" from topic %s - %s" % (msg.payload, msg.topic, repr(e)))

class MQTTDoorbotListener():

    def __init__(self):
        self.config = ConfigParser()
        self.config.read([
            'doorbot-listeners.conf',
            sys.path[0] + '/doorbot-listeners.conf',
            '/etc/doorbot-listeners.conf',
        ])

        self.acserver = ACServerLookup(self.config['default']['acserver'],
                                        self.config['default']['acserver_api_secret'])

        self.mqtt_client = mqtt.Client(userdata=self)
        self.mqtt_client.on_connect = on_mqtt_connect
        self.mqtt_client.on_message = on_mqtt_message

    def _mqtt_connect(self, client, flags, rc):
        topic = self.config['default']['mqtt_topic']
        print("Connected to server. Subscribing to %s" % (topic,))
        self.mqtt_client.subscribe(topic)

    def door_resolve(self, door):
        if door in self.config:
            if 'name' in self.config[door]:
                return self.config[door]
            else:
                print("Badly formed door entry - no name attribute")
        else:
            print("Unknown door %s" % (door,))
        # fall backto returning the name directly
        return {"name" : door}

    def _mqtt_message(self, client, msg):
        if len(msg.payload) == 0:
            print("Ignoring empty message")
            return
        # cut off the first / then split
        exploded_topic = msg.topic[1:].split('/')
        door = self.door_resolve(exploded_topic[1])
        action = exploded_topic[2]
        # payload should be json
        payload = json.loads(msg.payload.decode("utf-8"))
        if payload['Type'] == "RFID":
            card = payload['Card']
            (user,subscribed) = self.acserver.lookup_name(card)
            # if the card now has a name, it's valid. Otherwise, it's unknown

            if 'Granted' in payload: 
                if int(payload['Granted']) == 1:
                    self.on_card(card, user, door)
                else:
                    if len(user) == 0:
                        self.on_unknown_card(card, door, user)
                    else:
                        self.on_denied(card, user, door)
            else:
                if len(user) > 0:
                    self.on_card(card, user, door)
                elif not subscribed:
                    self.on_unknown_card(card, door, user)
                
        elif payload['Type'] == "START":
            self.on_start(door)
        elif payload['Type'] == "ALIVE":
            self.on_alive(door)
        elif payload['Type'] == "BELL":
            self.on_bell(door)
        elif payload['Type'] == "EXIT":
            self.on_exit(door)
        else:
            print("Unknown message type %s" % (payload['Type'],))

    # Implement any of these in your subclass. 
    # Door will be the config object
    def on_card(self, card_id, name, door):
        pass

    def on_denied(self, card_id, name, door):
        pass

    def on_unknown_card(self, card_id, door, user):
        pass

    def on_start(self, door):
        pass

    def on_alive(self, door):
        pass

    def on_bell(self, door):
        pass

    def on_exit(self, door):
        pass

    def run(self):
        self.mqtt_client.connect(self.config['default']['mqtt_server'])
        print("Running MQTT loop")
        while True:
            self.mqtt_client.loop()