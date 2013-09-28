import logging
import time
import serial

__all__ = ['Arduino', 'KMtronic', 'NothingRelay']

class SerialRelay(object):
    def __init__(self, port="/dev/ttyUSB0", speed=9600):
        self.ser = None
        self.port = port
        self.speed = speed

    def connect(self):
        self.ser = serial.Serial(self.port, self.speed)

    def disconnect(self):
        if self.ser:
            self.ser.close()
        self.ser = None


class Arduino(SerialRelay):
    def openDoor(self):
        self.ser.write('1')

    def checkBell(self):
        if self.ser.inWaiting() > 0:
            line = self.ser.readline()
            logging.debug('Response from serial: %s', repr(line))

            # empty buffer
            while self.ser.inWaiting() > 0:
                self.ser.read(1)

            if line.startswith("1"):
                logging.info('Doorbell pressed')
                return True

        return False

    def flashOK(self):
        self.ser.write("2"); # Green on
        self.ser.write("6"); # Piezo (Sleeps on the arduino for 3s)
        self.ser.write("3"); # Green off

    def flashBad(self):
        self.ser.write("4"); # Red on
        self.ser.write("6"); # Piezo (Sleeps on the arduino for 3s)
        self.ser.write("5"); # Red off


class KMtronic(SerialRelay):
    def openDoor(self):
        self.ser.write('\xff\x01\x01')
        time.sleep(0.5)
        self.ser.write('\xff\x01\x00')

    def checkBell(self):
        return False


class NothingRelay(object):
    def __init__(self, **kwargs):
        logging.info("relay: init: %s " % (str(kwargs)))

    def connect(self):
        logging.info("relay: connect")

    def disconect(self):
        logging.info("relay: disconnect")

    def openDoor(self):
        logging.info("relay: open door")
    
    def checkBell(self):
        logging.info("relay: check bell")
        return False

