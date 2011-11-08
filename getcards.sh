#!/bin/bash
cd `dirname $0`
curl -kf -o carddb.json.download --compressed https://london.hackspace.org.uk/carddb.php && mv carddb.json.download carddb.json
