#!/bin/bash

cd `dirname $0`
if [ ! -e /run/shm/carddb.json ]; then
cp carddb.json /run/shm
fi
