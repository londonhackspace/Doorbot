import socket
import select
import ipaddress
import paho.mqtt.client as mqtt
import json

def on_mqtt_connect(client, userdata, flags, rc):
    print("Connected to MQTT server")
    userdata._mqtt_connect(client, flags, rc)

def on_mqtt_message(client, userdata, msg):
    userdata._mqtt_message(client, msg)

class DoorbotForwarder:
    ''' 
    A class to listen on an interface and forward received doorbot
    messages to one or more other interfaces
    '''

    def __init__(self,
                listen_lan,
                sendinterfaces,
                ports,
                mqtt_server,
                mqtt_topic,
                mqtt_forward_map,
                mqtt_reverse_map):
        self.listen_lan = ipaddress.ip_network(listen_lan)
        self.sendinterfaces = sendinterfaces
        self.ports = ports
        self.mqtt_server = mqtt_server
        self.mqtt_topic = mqtt_topic
        self.mqtt_forward_map = mqtt_forward_map
        self.mqtt_reverse_map = mqtt_reverse_map

        # Scratch variables for internal state
        self.send_sockets = {}
        self.receive_sockets = {}

        # set up MQTT stuff
        self.mqtt_client = mqtt.Client(userdata=self)
        self.mqtt_client.on_connect = on_mqtt_connect
        self.mqtt_client.on_message = on_mqtt_message

    def _mqtt_connect(self, client, flags, rc):
        self.mqtt_client.subscribe(self.mqtt_topic)

    def _mqtt_message(self, client, msg):
        print("MQTT Message: " + str(msg.payload))
        json_msg = json.loads(msg.payload.decode("utf-8"))
        if json_msg['Source'] == "Bridge":
            print("Ignoring a message of our own")
            return
        # cut off the first / then split
        exploded_topic = msg.topic[1:].split('/')
        doorname = exploded_topic[1]
        action = exploded_topic[2]
        if not doorname in self.mqtt_reverse_map:
            print("Unknown door name %s - ignoring" % (doorname,))
            return
        port = self.mqtt_reverse_map[doorname]
        card = ""
        if "Card" in json_msg:
            card = json_msg["Card"]
        payload = (json_msg["Type"] + "\n" + card + "\n").encode("utf-8")
        self._send_payload(payload, port, True)


    def _send_payload(self, payload, port, from_mqtt = False):
        for interface, skt in self.send_sockets.items():
            print("Rebroadcasting on %s:%d" % (interface, port))
            skt.sendto(payload, ('255.255.255.255', port))
        
        if not from_mqtt:
            parts = payload.decode("utf-8").split('\n')
            msg = { "Type" : parts[0], "Card" : parts[1], "Source" : "Bridge" }
            if len(parts[2]) > 0:
                msg["Name"] = parts[2]
            topic = "/door/" + self.mqtt_forward_map[port] + "/status"
            self.mqtt_client.publish(topic, json.dumps(msg))

    def _handle_woken_socket(self, woken_socket):
        # iterate over receive_sockets to figure out which one was triggered
        # this is so we know the port to send on
        if woken_socket == self.mqtt_client.socket():
            self.mqtt_client.loop_read()
        for port, listen_skt in self.receive_sockets.items():
            if listen_skt == woken_socket:
                payload,(address, _) = woken_socket.recvfrom(1024)
                # we only want to forward packets that have come from
                # the source network - this is for two reasons:
                # 1) Avoid repeating our own packets in a loop
                # 2) A tiny bit of security
                if ipaddress.ip_address(address) in self.listen_lan:
                    print("Forwarding message from %s" % (address,))
                    self._send_payload(payload, port)
                # break here - we found the match for this inner loop
                break

    def start(self):
        '''
        Start the main loop of the forwarder
        '''
        for port in self.ports:
            print("Setting up listener for port %d" % (port,))
            skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            skt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            skt.bind(('', port))
            skt.setblocking(0)
            self.receive_sockets[port] = skt

        for sendinterface in self.sendinterfaces:
            print("Setting up sender for interface %s" % (sendinterface,))
            skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            skt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            skt.bind((sendinterface, 0))
            self.send_sockets[sendinterface] = skt

        self.mqtt_client.connect(self.mqtt_server)

        while True:
            skts = list(self.receive_sockets.values())
            skts.append(self.mqtt_client.socket())
            result = select.select(skts, [self.mqtt_client.socket()], [], 5.0)
            for in_skt in result[0]:
                self._handle_woken_socket(in_skt)
            for in_skt in result[1]:
                self.mqtt_client.loop_write()
            self.mqtt_client.loop_misc()

