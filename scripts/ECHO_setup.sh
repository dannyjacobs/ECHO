#!/bin/bash

echo -n "Enter MAVProxy connection port: "
read port

echo -n "Enter Baud rate: "
read baud

mavproxy.py --master=/dev/tty.$port --baudrate=$baud --out=udp.127.0.0.1:14550 --out=udp.127.0.0.1:14551 &
pid1 = $!

sleep10 ;

open /Applications/APM\ Planner\ 2.0.app/

#wait $pid1
