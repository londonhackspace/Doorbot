#!/bin/bash
curl -kf -o carddb.json.download --compressed https://london.hackspace.org.uk/carddb.php && mv carddb.json.download carddb.json
