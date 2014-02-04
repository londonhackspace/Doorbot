#!/bin/bash
cd /run/shm
curl -s -S -kf -o carddb.json.download --compressed https://london.hackspace.org.uk/carddb.php && mv carddb.json.download carddb.json
#curl -kf -o carddb.json.download --compressed https://85.119.83.146/carddb.php && mv carddb.json.download carddb.json
