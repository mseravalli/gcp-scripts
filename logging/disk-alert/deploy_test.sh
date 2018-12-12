#!/bin/zsh -x

/usr/local/bin/functions clear
/usr/local/bin/functions deploy json2xml --trigger-http
/usr/local/bin/functions call json2xml --data="$(cat ./event_test.js)"
/usr/local/bin/functions logs read -l 100
