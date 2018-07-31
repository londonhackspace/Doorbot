import socket
import select
import ipaddress

class DoorbotForwarder:
    ''' 
    A class to listen on an interface and forward received doorbot
    messages to one or more other interfaces
    '''

    def __init__(self, listen_lan, sendinterfaces, ports):
        self.listen_lan = ipaddress.ip_network(listen_lan)
        self.sendinterfaces = sendinterfaces
        self.ports = ports

        # Scratch variables for internal state
        self.send_sockets = {}
        self.receive_sockets = {}

    def _send_payload(self, payload, port):
        for interface, skt in self.send_sockets.items():
            print("Rebroadcasting on %s:%d" % (interface, port))
            skt.sendto(payload, ('255.255.255.255', port))

    def _handle_woken_socket(self, woken_socket):
        # iterate over receive_sockets to figure out which one was triggered
        # this is so we know the port to send on
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

        while True:
            result = select.select(self.receive_sockets.values(), [], [])
            for in_skt in result[0]:
                self._handle_woken_socket(in_skt)

