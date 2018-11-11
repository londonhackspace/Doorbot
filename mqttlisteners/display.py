#!/usr/bin/env python
# encoding=utf-8

import time, random, logging, os, urllib

class display:
  def __init__(self, host="net-o-meter.local."):
    self.host = "http://" + host + "/"
    logging.basicConfig()
    self.l = logging.getLogger(__name__)
    self.isdead = False
    self.start()
    self.state = ['','','','']

  def reinit(self):
    pass

  def send(self, thing):
    ok = False
    try:
      f = urllib.request.urlopen(self.host + thing)
      ret = f.read()
      ret = ret.decode("ascii")
      if ret != "Ok":
        self.l.error(self.host + thing + " -> " + ret)
      ok = True
    except Exception as e:
      # don't log errors if we are already dead
      if not self.isdead:
        self.l.exception("bandwidth meter has died? exception in send: ")
        self.isdead = True

    if ok and self.isdead:
      self.l.error("bandwidth meter: " + self.host + thing + " is working now")
      self.isdead = False

  def clear(self):
    self.send("v/c")

  def start(self):
    self.clear()
    self.send("v/p?0,0")
    self.state = ['','','','']

  def pos(self, h, v):
    wstr = "v/p?%d,%d" % (h,v)
    self.send(wstr)

  def centered(self, str, h=1):
    x = (20 - len(str)) / 2
    self.pos(x,h)
    self.write(str)

  def left(self, str, h=1):
    self.pos(0,h)
    self.write(str)

  def write(self, str):
    str = str.replace("£", chr(0xf8))
    out = "v/w?" + urllib.parse.quote(str)
    self.send(out)

  def top(self, val):
    if val > 16:
      val = 16
    self.send("s/t?%d" % (val))

  def bottom(self, val):
    if val > 16:
      val = 16
    self.send("s/b?%d" % (val))

  def strip(self, strip, vals):
    assert len(vals) == 16, "only 16 leds per strip!"
    out = "s/set?" + strip + ''.join(vals)
    assert len(out) == 6 + 1 + (16 * 3), "wrong length of something!"
    self.send(out)

  def close(self):
    pass

def randcol():
  return "%x%x%x" % (random.randint(0,15), random.randint(0,15), random.randint(0,15))

if __name__ == "__main__":
  d = display()
  d.start()
  d.top(0)
  d.bottom(0)

  ttuple = time.localtime()
  date = time.strftime("%a %e %b", ttuple)
  d.centered(date, 0)

  t = time.time()

  otstr = odate = "fish"

  d.clear()

  d.write("That will be £42.20")

#  while True:
#    time.sleep(20)

  i = 0
#  while True:
#    off = 20
#    if i + off > 255:
#      off = 255 - i
#    o = [chr(x) + " %02x" % (x) for x in range(i, i + off)]
#    o = "".join(o)
#    d.write(o)
#    if off != 20:
#      i = 0
#    else:
#      i += 20
#    time.sleep(2)


  while True:
    ttuple = time.localtime()
    tstr = time.strftime("%H:%M:%S", ttuple)
    date = time.strftime("%a %e %b",ttuple)
    if date != odate:
      d.centered(date, 0)
      odate = date
    if tstr != otstr:
      d.centered(tstr, 2)
      otstr = tstr

    time.sleep(0.1)

    nt = time.time()
    if True: #(nt - t) > 1:
      t = time.time()
      a = randcol()
      b = randcol()
      z = [a for i in range(0,random.randint(0,14))]
#      print z
      d.strip('t', z + [b for i in range(0, 16 - len(z))])

#      a = randcol()
#      b = randcol()
#      z = [a for i in range(0,random.randint(0,14))]

#      z = ["%x00" % (i) for i in range(0,16)]

#      r1,g1,b1 = (random.randint(0,15), random.randint(0,15), random.randint(0,15))
#      r2,g2,b2 = (random.randint(0,15), random.randint(0,15), random.randint(0,15))

#      z = ["%x%x%x" % ( (abs(r2-r1) / 16.0) * i, (abs(g2-g1) / 16.0) *i, (abs(b2-b1) / 16.0) * i) for i in range(0,16)]
#      print z
#      d.strip('b', z)

      d.strip('t', [randcol() for i in range(0,16)])
      d.strip('b', [randcol() for i in range(0,16)])

#      d.send("b%d" % (random.randint(1,16)) )
#      d.send("t%d" % (random.randint(1,16)) )
#      if random.randint(1,10) == 1:
#        d.send("e")

  d.close()
