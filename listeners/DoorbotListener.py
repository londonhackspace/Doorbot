import select, socket

class DoorbotListener():

    def listen(self, port=50000):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('<broadcast>', port))
        s.setblocking(0)

        while True:

            try:

                result = select.select([s],[],[])
                payload = result[0][0].recv(1024)
                (event, serial, name) = payload.split("\n")

                if (event == 'RFID' and name):
                    self.doorOpened(serial, name)

                elif (event == 'RFID' and not name):
                    self.unknownCard(serial)

                elif (event == 'BELL'):
                    self.doorbell()

                elif (event == 'START'):
                    self.startup()

		#for triggering sounds, the "serial" field is just the name of a .wav file
		elif (event == "TRIGGER"):
	            self.trigger(serial)

            except Exception, e:
                pass


    def doorOpened(self, serial, name):
        pass

    def unknownCard(self, serial):
        pass

    def doorbell(self):
        pass

    def startup(self):
        pass

    def trigger(self, serial):
        pass

