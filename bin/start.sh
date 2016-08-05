#!/bin/bash

echo "Starting RSS Grabber backend ..."
python ../server.py start &> ../backend.log &
echo $! > /tmp/rssgrab.pid
echo "RSS Grabber backend ... started"

echo "Starting RSS Grabber frontend ..."
./../client/node_modules/gulp/bin/gulp.js serve &> ../frontend.log &
echo $! > /tmp/rssgrab_front.pid
echo "RSS Grabber frontend ... started"
