#!/bin/sh

# yuck

cd /root/Doorbot/listeners

for script in doorbot-glados.py doorbot-boarded.py ; do
	screen -S $script -d -m -t $script bash -c "python /root/Doorbot/listeners/${script} ; exec bash "
done
