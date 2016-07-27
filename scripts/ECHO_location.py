#! /usr/bin/env python
from pymavlink import mavutil
from astropy.time import Time
from time import sleep
import sys

filename = sys.argv[1]

byte_count = 0 # initial byte count is zero (beginning of file)
SLEEP_TIME = 0.1

try:
    while True:
      mlog = mavutil.mavlink_connection(filename)
      start_time = Time(mlog.start_time,format='unix').gps
      mlog.f.seek(byte_count) # go to current byte count offset
      pos = mlog.recv_match(type='GPS_RAW_INT',blocking=False)
      if not pos is None:
        byte_count = mlog.f.tell() # update current byte count offset
        timestamp = start_time + pos.time_usec*1e-6
        print timestamp,pos.lat*1e-07,pos.lon*1e-07,pos.alt
        sleep(SLEEP_TIME)

      while not pos is None:
        pos = mlog.recv_match(type='GPS_RAW_INT',blocking=False)
        if not pos is None: # Check if position received
            byte_count = mlog.f.tell() # update current byte count offset
            timestamp = start_time + pos.time_usec*1e-6
            print timestamp,pos.lat*1e-07,pos.lon*1e-07,pos.alt
            sleep(SLEEP_TIME)
        else:
            print '\nRe-reading %s <(''^) ^(' ')^ (^'')>...\n' %filename
except(KeyboardInterrupt):
    print '\nExiting...\n'
    sys.exit()
