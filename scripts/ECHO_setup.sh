#!/bin/bash

echo -n "Enter MAVProxy connection port: "
read port

echo -n "Enter Baud rate: "
read baud

echo -n "Enter APM Planner 2.0 location: "
read apm_loc

mavproxy.py --master=/dev/tty.$port --baudrate=$baud --out=udp.127.0.0.1:14550 --out=udp.127.0.0.1:14551 &
pid1 = $!

sleep 5 ;

open $apm_loc/APM\ Planner\ 2.0.app/
