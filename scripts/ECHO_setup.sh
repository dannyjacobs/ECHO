#!/bin/bash

echo -n "Enter MAVProxy connection port: (i.e. /dev/tty.usb*)"
read port

echo -n "Enter Baud rate: (57600 for 3DR radio)"
read baud

echo -n "Enter APM Planner 2.0 location: (i.e. /Applications) "
read apm_loc

open $apm_loc/APM\ Planner\ 2.0.app/

mavproxy.py --master=$port --baudrate=$baud --out=udp:127.0.0.1:14550 --out=udp:127.0.0.1:14551 
