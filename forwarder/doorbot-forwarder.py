import configparser
import DoorbotForwarder
import sys

listen_lan = None
send_interfaces = []
ports = []

config = configparser.ConfigParser()
config.read([
            'doorbot-forwarder.conf',
            sys.path[0] + '/doorbot-forwarder.conf',
            '/etc/doorbot-forwarder.conf'])

mqtt_map_config = configparser.ConfigParser()
mqtt_map_config.read([
            'mqtt-map.conf',
            sys.path[0] + '/mqtt-map.conf',
            '/etc/mqtt-map.conf'])

mqtt_forward_map = {}
mqtt_reverse_map = {}

for key, val in mqtt_map_config['forward'].items():
    mqtt_forward_map[int(key)] = val

for key, val in mqtt_map_config['reverse'].items():
    mqtt_reverse_map[key] = int(val)

listen_lan = config['default']['listen_lan']
ports = list(map(int, config['default']['ports'].split(',')))
mqtt_topic = config['default']['mqtt_topic']
mqtt_server = config['default']['mqtt_server']

for name, entry in config.items():
    if name != "DEFAULT" and name != 'default':
        send_interfaces.append(entry['interface'])

if listen_lan is None or len(send_interfaces) == 0 or len(ports) == 0:
    print("Please specify sources and destinations")
    exit(1)

forwarder = DoorbotForwarder.DoorbotForwarder(listen_lan,
                                                send_interfaces,
                                                ports,
                                                mqtt_server,
                                                mqtt_topic,
                                                mqtt_forward_map,
                                                mqtt_reverse_map)
forwarder.start()
