#!/bin/bash

#
# XXX is this the best place to put these?
#
# symlink traversal attack?
#

cd /root/Doorbot
curl -s -S -kf -o carddb.json.download --compressed https://london.hackspace.org.uk/carddb.php > getcards.err 2>&1

if [ $? -eq 0 ] ; then
	mv carddb.json.download carddb.json
	if [ -e getcards.haderrors ] ; then
		echo "doorbot is working now"
		rm -f getcards.haderrors
	fi
else
	if [ ! -e getcards.haderrors ] ; then
		echo "doorbot problems: "
		echo
		cat getcards.err ; rm -f getcards.err
		echo ; echo "Further emails suppresed until getcards is working again"
		touch getcards.haderrors
	fi
fi
