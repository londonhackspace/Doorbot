#!/usr/bin/env python
#
#
#

class historylist:
  def __init__(self, length):
    self.data = list()
    self.length = length
    self.pos = 0

  def append(self, thing):
    if len(self.data) < self.length:
      self.data.append(thing)
    else:
      self.data[self.pos] = thing
      self.pos += 1
      if self.pos >= self.length:
        self.pos = 0

  def average(self):
    total = sum(self.data)
    return float(total) / len(self.data)

  def min(self):
    return min(self.data)

  def max(self):
    return max(self.data)

  def full(self):
    return len(self.data) == self.length

  def __repr__(self):
    return "<listlist: len: %d items %d>" % (self.length, len(self.data))


if __name__ == "__main__":
  hl = historylist(42)
  print(hl)
  hl.append(0)
  print(hl)
  for i in range(0, 100):
    hl.append(42)
  print(hl)
  print((hl.max()))
  print(hl.min())
  print(hl.average())
  print(len(hl.data))

  import random

  for i in range(0, 40):
    hl.append(random.randint(0, 100))
  print(hl)
  print(hl.max())
  print(hl.min())
  print(hl.average())
  print(len(hl.data))
  print(hl.data)
