#!/bin/bash
# This is for the docker container to allow vnc interaction with the docker internal browser
Xvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 & 
sleep 1
x11vnc -display :99 -forever -nopw -rfbport 5900 > /dev/null 2>&1 &
sleep 1
websockify --web /usr/share/novnc 6080 localhost:5900 > /dev/null 2>&1 &
sleep 1
echo "VNC websocket started at localhost:6080"
DISPLAY=:99 python scrape.py
