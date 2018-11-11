#!/usr/bin/env python
#
# The intention here is to produce a colour for a given nick that we can display on the 
# net-o-meter colour strips.
#
# It's supposed to use the same algo as pidgin does so that people colours are
# the same as someone using pidgin for irc would see.
#
# I did think at one point that there was an unofficial standard
# for colourising a nick, but this dosn't appear to be the case.
#
# as a result this code is a bit pointless...
#
# I guess we could associate a colour with a space member the
# same way we have a glados noise...
#

import random, time, ctypes

nickcols = []

# pidgin/gtknickcolors.h

nick_seed_colours = [
        (0, 64764, 59881, 20303),       # Butter #1 
        (0, 60909, 54484, 0),           # Butter #2 
        (0, 50372, 41120, 0),           # Butter #3 
        (0, 64764, 44975, 15934),       # Orange #1 
        (0, 62965, 31097, 0),           # Orange #2 
        (0, 52942, 23644, 0),           # Orange #3 
        (0, 59811, 47545, 28270),       # Chocolate #1 
        (0, 49601, 32125, 4369),        # Chocolate #2 
        (0, 36751, 22873, 514),         # Chocolate #3 
        (0, 35466, 58082,  13364),      # Chameleon #1 
        (0, 29555, 53970, 5654),        # Chameleon #2 
        (0, 20046, 39578, 1542),        # Chameleon #3 
        (0, 29289, 40863, 53199),       # Sky Blue #1 
        (0, 13364, 25957, 42148),       # Sky Blue #2 
        (0, 8224, 19018, 34695),        # Sky Blue #3 
        (0, 44461, 32639, 43167),       # Plum #1 
        (0, 30069, 20560, 31611),       # Plum #2  
        (0, 23644, 13621, 26214),       # Plum #3 
        (0, 61423, 10537,  10537),      # Scarlet Red #1 
        (0, 52428, 0, 0),               # Scarlet Red #2 
        (0, 42148, 0, 0),               # Scarlet Red #3 
        (0,  34952, 35466,  34181),     # Aluminium #4
        (0,  21845, 22359,  21331),     # Aluminium #5
        (0,  11822, 13364,  13878)      # Aluminium #6
]

#define DEFAULT_SEND_COLOR "#204a87"
#define DEFAULT_HIGHLIGHT_COLOR "#AF7F00"

NUM_NICK_COLORS = 220

#
# to be compatible we need libc srand/rand.
# which python dosn't seem to have anymore (?)
#
# rip portability :,(
#
LIBC = ctypes.cdll.LoadLibrary("libc.so.6")

def srand(seed):
  LIBC.srand(seed)

def rand():
  return LIBC.rand()

#
# pidgin uses g_str_hash, which uses djb's hash, which apperently is
# popular or something.
#
# this is copied from:
# https://code.google.com/p/python-pure-cdb/source/browse/cdblib.py
#
def djb_hash(s):
  '''Return the value of DJB's hash function for the given 8-bit string.'''
  h = 5381
  for c in s:
    h = (((h << 5) + h) ^ ord(c)) & 0xffffffff
  return h # for small strings, masking here is faster.

#
# The algo is:
#
# http://hg.pidgin.im/pidgin/main/file/6c2fa6d8037d/pidgin/gtkconv.c#l11011
#
# this is not a complete impelementation of it.
#
def generate_nick_colours():
  # white background.
  srand(255+255+255+1)
  numcolours = NUM_NICK_COLORS
  i = 0
  j = 0

#  breakout_time = time.time() + 3
#  while (i < numcolours and j < len(nick_seed_colours) and time.time() < breakout_time):
#    colour = nick_seed_colours[j]
#    nickcols[i] = colour
#    j++

  while i < numcolours:
    colour = (0, rand() % 65536, rand() % 65536, rand() % 65536)
    nickcols.append(colour)
    i += 1

def nick2colour(nick):
  if len(nickcols) == 0:
    generate_nick_colours()
  nickcols[djb_hash(nick) % len(nickcols)]
  # argb presumably, we don't need the a.
  col =  nickcols[djb_hash(nick) % len(nickcols)]
  return (col[1], col[2], col[3])

def sixteenbit2fourbitcolour(col):
  col = "%01x%01x%01x" % (col[0] >> 12, col[1] >> 12 , col[2] >> 12)
  return col

if __name__ == "__main__":
  for name in ["jasperw", "fishfish", "fishfish2", "abscond", "Akki14"]:
    print("%-20s %s" % (name, sixteenbit2fourbitcolour(nick2colour(name))))

