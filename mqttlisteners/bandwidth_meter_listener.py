#!/usr/bin/env python
#
# originaly from https://github.com/londonhackspace/net-o-meter, in the
# 'client' dir.
#

import os, sys, time, textwrap, argparse, threading, queue
from display import display
from histlist import historylist
from nickcolors import sixteenbit2fourbitcolour, nick2colour
from iftable import get_speeds_snmp
from MQTTDoorbotListener import MQTTDoorbotListener

from irc_listener import strip_string

class BmeterDoorbotListener(MQTTDoorbotListener):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def on_card(self, card_id, name, door, gladosfile):
        if not door.getboolean('announce', True):
            return

        name = strip_string(name)
        msg = "%s opened %s" % (name, door['name'])

        self.send_message(['RFID', name, msg])

    def on_unknown_card(self, card_id, door):
        self.send_message(['unknown', None, "Unknown card presented to %s" % (door['name'],)])

    def on_start(self, door):
        self.send_message(['start', None, "MQTT Bmeter thing starting."])

    def on_alive(self, door):
        pass

    def on_denied(self, card_id, name, door):
        self.send_message(['denied', strip_string(name), "access denied to %s for %s" % (door['name'], strip_string(name))])

    def on_bell(self, door):
        dingdong = 'DING DONG, DOOR BELL!'
        self.send_message(['BELL', None, "%s: %s" % (door['name'], dingdong)])

    def send_message(self, message):
        self.queue.put_nowait(message)

class Speed:
    def __init__(self, callback, args, inspeed, outspeed, period = 5):
        self.cb = callback
        self.args = args
        self.inspeed = None
        self.outspeed = None
        self.lasttime = None
        self.time = None
        self.in_max_speed = inspeed
        self.out_max_speed = outspeed
        self.lastin = None

        # the period is wrong here cos of snmptable being slow,
        # need to do this properly
        #
        # the period isn't right (it changes with how
        # slow snmptable is or isn't).
        #
        # need to have histlist know it's length in time
        # and discard samples older than the duration we are interested in.
        #
        self.iminlist = historylist(60 / period)
        self.itenminlist = historylist(600 / period)

        self.ominlist = historylist(60 / period)
        self.otenminlist = historylist(600 / period)

    def update(self):
        inspeed, outspeed = self.cb(*self.args)
        if inspeed == None or outspeed == None:
            # didn't get it for some reason
            return
        self.lastin = self.inspeed
        self.lastout = self.outspeed
        self.inspeed, self.outspeed = inspeed, outspeed
        self.lasttime = self.time
        self.time = time.time()

    def speed_diff(self, ospeed, nspeed):
        # counter roll over
        # XXX python types vs. 2**32?
        if nspeed < ospeed:
            nspeed += 2 ** 32
        return nspeed - ospeed

    def rate(self):
        for t in self.inspeed, self.outspeed, self.lastin, self.time, self.lasttime:
            if t == None:
                return (None, None)

        period = self.time - self.lasttime
        inspeed = self.speed_diff(self.lastin, self.inspeed) / period
        outspeed = self.speed_diff(self.lastout, self.outspeed) / period
        self.iminlist.append(inspeed)
        self.ominlist.append(outspeed)
        self.itenminlist.append(inspeed)
        self.otenminlist.append(outspeed)
        return (inspeed, outspeed)

    def onemin(self):
        return (self.iminlist.average(), self.ominlist.average())

    def onemin_mbit(self):
        return (self.mbit(self.iminlist.average()),
                self.mbit(self.ominlist.average()))

    def tenmin(self):
        return (self.itenminlist.average(), self.otenminlist.average())

    def tenmin_mbit(self):
        return (self.mbit(self.itenminlist.average()),
                self.mbit(self.otenminlist.average()))

    def mbit(self, speed):
        if speed == None:
            return "0.0"
        speed = speed  * 8.0 # bits
        speed = speed / float(1000 * 1000) # mbit
        return "%.2f" % (speed)

    def rate_mbit(self):
        inspeed, outspeed = self.rate()
        return (self.mbit(inspeed), self.mbit(outspeed))

    def display_mangle(self, speed, link_speed):
        link = link_speed / 16.0
        speed = int(float(speed) / link)
        return speed

    def rate_display(self):
        # also busted period
        inspeed, outspeed = self.rate_mbit()
        ret = []
        for rate, link_speed in ((inspeed, self.in_max_speed), (outspeed, self.out_max_speed)):
            ret.append(self.display_mangle(rate, link_speed))
        return ret

    def onemin_display(self):
        inspeed, outspeed = self.onemin_mbit()
        ret = []
        for rate, link_speed in ((inspeed, self.in_max_speed), (outspeed, self.out_max_speed)):
            ret.append(self.display_mangle(rate, link_speed))
        return ret

    def tenmin_display(self):
        inspeed, outspeed = self.tenmin_mbit()
        ret = []
        for rate, link_speed in ((inspeed, self.in_max_speed), (outspeed, self.out_max_speed)):
            ret.append(self.display_mangle(rate, link_speed))
        return ret

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Display bandwidth usage on the bandwidth meter.')
    parser.add_argument('--host', type=str, nargs=1, metavar=('<hostname>'),
      help='the host to read bandwidth from')

    parser.add_argument('--community', type=str, nargs=1, metavar=('<community>'),
      help='SNMP community name to use')

    args = parser.parse_args()

    print("net-o-meter starting up.")

    q = queue.Queue(42)
    dbl = BmeterDoorbotListener(q)
    dblthread = threading.Thread(name="bmeter_mqtt", target=dbl.run)
    dblthread.setDaemon(True)
    dblthread.start()

    d = display(host="bmeter.lan.london.hackspace.org.uk")
    d.clear()
    d.start()
    d.bottom(0)
    d.top(0)
    d.centered("inbound", 0)
    d.centered("outbound", 2)

    ttuple = time.localtime()
    date = time.strftime("%a %e %b", ttuple)
    d.centered(date, 1)

    if 'hostname' in args:
        host = args.hostname
    else:
        host = 'boole'


    period = 5
    tperiod = period # target period

    # Ujima House, allegedly 300 / 300
    ujimaiface = Speed(get_speeds_snmp, [host, 'em0'], 300.0, 300.0)

    ifaces = [["Ujima Net", ujimaiface, 0],]

    for ispname, iface, c in ifaces:
        iface.update()

    ntime = time.time()
    time.sleep(period)

    state = "bw"
    statecount = 0

    event = name = msg = None
    iselect = 0
    changed = True
    nchunks = None
    colour = None

    wrapper = textwrap.TextWrapper(width=20, expand_tabs=False)

    while True:
        for ispname, iface, c in ifaces:
            iface.update()
        otime = ntime
        ntime = time.time()

        ispname, iface, counter = ifaces[iselect]
        ifaces[iselect][2] += 1
        if iselect == 1:
            iselect = 0
        else:
            if len(ifaces) > 1:
                iselect = 1

        ispeed, ospeed = iface.rate_mbit()
        indisplay, outdisplay = iface.rate_display()

        legend = "%d Secs sample" % (tperiod)

        # every other time
        if counter % 2 and iface.ominlist.full():
            (ispeed, ospeed) = iface.onemin_mbit()
            indisplay, outdisplay = iface.onemin_display()
            legend = "1 Min average"

        if ((counter % 6) == 0) and iface.otenminlist.full():
            (ispeed, ospeed) = iface.tenmin_mbit()
            indisplay, outdisplay = iface.tenmin_display()
            legend = "10 Min average"

        # these are in and out on the port
        t = "Down " + str(ispeed) + " Mbits"
        b = "Up   " + str(ospeed) + " Mbits"

        d.clear()

        if state == "card" and name:
            if changed:
                name = name.replace('\n', ' ')
                colour = sixteenbit2fourbitcolour(nick2colour(name))

                # the display is 20 chars accross
                nchunks = wrapper.wrap(msg)
                if len(nchunks) > 3:
                    nchunks = nchunks[0:3]
            y = 0
            for n in nchunks:
                d.left(n, y)
                y += 1
            d.strip('t', (colour,) * 16)
            d.strip('b', (colour,) * 16)
        elif state == "bell":
            if changed:
                # the display is 20 chars accross
                nchunks = wrapper.wrap(msg)
                if len(nchunks) > 3:
                    nchunks = nchunks[0:3]
            y = 0
            for n in nchunks:
                d.left(n, y)
                y += 1

            d.strip('t', ('000', '0f0') * 8)
            d.strip('b', ('0f0', '000') * 8)
        elif state == 'bw':
            d.left(t, 0)
            d.left("ISP: " + ispname, 1)
            d.left(b, 2)
            d.left(legend, 3)
            d.top(indisplay)
            d.bottom(outdisplay)
        else:
            if changed:
                if name:
                  name = name.replace('\n', ' ')
                  colour = sixteenbit2fourbitcolour(nick2colour(name))
                else:
                  color = 'f00'

                # the display is 20 chars accross
                nchunks = wrapper.wrap(msg)
                if len(nchunks) > 3:
                    nchunks = nchunks[0:3]
            y = 0
            for n in nchunks:
                d.left(n, y)
                y += 1
            d.strip('t', (colour,) * 16)
            d.strip('b', (colour,) * 16)

        if statecount > 0:
            statecount -= 1
            if statecount == 0:
                state = "bw"

        real_period = ntime - otime

        pdiff = real_period - period
        period = tperiod - pdiff

        if period < 2:
            continue

        changed = False
        payload = None
        try:
          payload = q.get_nowait()
        except queue.Empty:
          pass

        if payload is not None:
            changed = True
            (event, name, msg) = payload

            print(("%s %s %s" % (event, name, msg)))

            if event == 'RFID' and name:
                state = "card"
                statecount = 2
            elif event == 'BELL':
                state = "bell"
                statecount = 2
            else:
                state = event
                statecount = 2
