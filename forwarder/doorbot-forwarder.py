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

listen_lan = config['default']['listen_lan']
ports = list(map(int, config['default']['ports'].split(',')))

for name, entry in config.items():
    if name != "DEFAULT" and name != 'default':
        send_interfaces.append(entry['interface'])

if listen_lan is None or len(send_interfaces) == 0 or len(ports) == 0:
    print("Please specify sources and destinations")
    exit(1)

forwarder = DoorbotForwarder.DoorbotForwarder(listen_lan, send_interfaces, ports)
forwarder.start()
