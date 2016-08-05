#!/bin/bash

echo "Stopping RSS Grabber backend ..."
if [ -e "/tmp/rssgrab.pid" ]
then
  kill `cat /tmp/rssgrab.pid`
  rm /tmp/rssgrab.pid
  echo "RSS Grabber backend stopped"
else
    echo "RSS Grabber is not running"
fi

echo "Stopping RSS Grabber frontend ..."
if [ -e "/tmp/rssgrab_front.pid" ]
then
  kill `cat /tmp/rssgrab_front.pid`
  rm /tmp/rssgrab_front.pid
  echo "RSS Grabber frontend stopped"
else
    echo "RSS Grabber frontend is not running"
fi
