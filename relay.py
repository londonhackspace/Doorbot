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
    def openDoor(self, duration=None):
        self.ser.write('1')

    def checkBell(self):
        if self.ser.inWaiting() > 0:
            line = self.ser.readline()
            logging.info('Response from serial: %s', repr(line))

            # empty buffer
            tmp = ""
            while self.ser.inWaiting() > 0:
                tmp += self.ser.read(1)

            logging.info('Extra from serial: %s', repr(tmp))
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
    def openDoor(self, duration=2):
        self.ser.write('\xff\x01\x01')
        time.sleep(duration)
        self.ser.write('\xff\x01\x00')

    def checkBell(self):
        self.ser.write('\xff\x01\x00')
        return False


class NothingRelay(object):
    def __init__(self, **kwargs):
        logging.debug("relay: init: %s " % (str(kwargs)))

    def connect(self):
        logging.debug("relay: connect")

    def disconnect(self):
        logging.debug("relay: disconnect")

    def openDoor(self, duration=None):
        logging.debug("relay: open door, duration %s", duration)

    def checkBell(self):
        logging.debug("relay: check bell")
        return False

