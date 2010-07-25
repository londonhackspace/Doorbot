#!/usr/bin/python

#  readmifaresimple.py - read all sectors from a mifare tag
# 
#  Adam Laurie <adam@algroup.co.uk>
#  http://rfidiot.org/
# 
#  This code is copyright (c) Adam Laurie, 2006, All rights reserved.
#  For non-commercial use only, the following terms apply - for all other
#  uses, please contact the author:
#
#    This code is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#

import sys
import os
import RFIDIOtconfig
import time

try:
	card= RFIDIOtconfig.card
except:
	os._exit(False)

args= RFIDIOtconfig.args
help= RFIDIOtconfig.help

blocksread= 0
blockslocked= 0
lockedblocks= []
DEFAULT_KEY= 'FFFFFFFFFFFF'
DEFAULT_KEYTYPE= 'AA'
BLOCKS_PER_SECT= 4
START_BLOCK= 0
END_BLOCK= 64

if help or len(args) > 4:
        print sys.argv[0] + ' - test read a mifare tag'
        print 'Usage: ' + sys.argv[0] + ' [START BLOCK] [END BLOCK] [KEY] [KEYTYPE]'
        print
        print '\tRead Mifare sector numbers [START BLOCK] to [END BLOCK], using' 
        print '\t[KEY] to authenticate. Keys can be truncated to \'AA\' for transport' 
        print '\tkey \'A0A1A2A3A4A5\', \'BB\' for transport key \'B0B1B2B3B4B5\' or \'FF\''
        print '\tfor transport key \'FFFFFFFFFFFF\'.' 
	print 
        print '\tSTART BLOCK defaults to 0 and END BLOCK to 64. If not specified, KEY'
	print '\tdefaults to \'FFFFFFFFFFFF\', and KEYTYPE defaults to \'AA\'.' 
	print 
	print '\tThis program demonstrates the different techniques required to read'
	print '\tMifare tags on different readers.'
        print
        os._exit(True)

card.info('readmifaresimple v0.1d')

if not card.select():
	print '  No card detected!'
	os._exit(False)

# set options
try:
	keytype= args[3]
except:
	 keytype= DEFAULT_KEYTYPE
try:
	key= args[2]
except:
	key= DEFAULT_KEY
try:
	endblock= int(args[1])
except:
	endblock= END_BLOCK
try:
	startblock= int(args[0])
except:
	startblock= 0

card.select()
print '  Card ID:', card.uid
print
print '    Reading from %02d to %02d, key %s\n' % (startblock, endblock, key)

# see if key is an abbreviation
# if so, only need to set keytype and login will use transport keys
for d in ['AA','BB','FF']:
	if key == d:
		keytype= key
		key= ''

block = startblock
while block < endblock:
	locked= True
        print '    Block %03i: ' % block,
	# ACG requires a login only to the base 'sector', so block number must be divided
	# by BLOCKS_PER_SECT
	if card.readertype == card.READER_ACG:
		loginblock= block / BLOCKS_PER_SECT
	else:
		loginblock= block
	if card.login(loginblock,keytype,key):
		print 'Login OK. Data:',
		locked= False
#		time.sleep(0.2)
		if card.readMIFAREblock(block):
			blocksread += 1
			print card.MIFAREdata,
			print card.ReadablePrint(card.ToBinary(card.MIFAREdata))	
		else:
			print 'Read error: %s %s' % (card.errorcode , card.ISO7816ErrorCodes[card.errorcode])
	else:
		print 'Login error: %s %s' % (card.errorcode , card.ISO7816ErrorCodes[card.errorcode])
		locked= True
		blockslocked += 1
		lockedblocks.append(block)
		# ACG requires re-select to clear error condition after failed login
		if card.readertype == card.READER_ACG:
			card.select()
        block +=  1

print
print '  Total blocks read: %d' % blocksread
print '  Total blocks locked: %d' % blockslocked
if blockslocked > 0:
	print '  Locked block numbers:', lockedblocks
