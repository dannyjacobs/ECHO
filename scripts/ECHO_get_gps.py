'''

    Author: Jacob Burba

    ECHO_Get_GPS.py connects to a drone via MAVLink Micro Air Vehicle Communication Protocol and
    obtains the GPS positions of the drone in realtime.  A telemetry radio must be plugged in to the
    machine running this code to obtain a proper connection.  Additionally, ECHO_setup.sh must also
    be run prior to executing this code to ensure that the drone is broadcasting on two UDP channels,
    being 127.0.0.1:14550 and 127.0.0.1:14551.  The former is for communication with APM Planner
    while the latter channel is used for communication the machine running this code.

    When running this code, the user needs to pass a file name for the GPS positions and correspon-
    ing times to be written to.  The execution of this can be seen in the following example

                python ECHO_Get_GPS.py --gps_file=<output_filename> --trans=EW

    The generated output file can then be passed to ECHO_accumulate.py in which it will be stitched
    together with corresponding spectral data.

'''

import sys,os,optparse
import numpy as np
import time
from pymavlink import mavutil
#from ECHO_position_utils import get_position
from ECHO_time_utils import unix_to_gps,gps_to_HMS
from astropy.time import Time


o = optparse.OptionParser()
o.set_description('Takes raw APM/Orbcomm data and creates an interpolated, combined text file')
o.add_option('--gps_file',type=str,
    help='File name for output of GPS data')
o.add_option('--tlog',type=str,
    help='APM tlog file path')
o.add_option('--trans',type=str,
    help='Transmitting antenna polarization')
opts,args = o.parse_args(sys.argv[1:])


# Establish connection with Drone via UDP
#udp = mavutil.mavudp('127.0.0.1:14551')

''' TESTING READING TLOG FROM APM PLANNER '''
byte_count = 0 # initial byte count is zero (beginning of file)
SLEEP_TIME = 0.1
TIME_SINCE_BOOT_FACTOR = 1e-06

'''
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
'''

# Setup outfile
dt = 0.2 # time delay between GPS messages
date = time.strftime('%m_%d_%Y')
currtime = time.strftime('%H:%M:%S') # 24 Hr format
header = '# GPS Positions file for '+date+', '+currtime
if opts.trans:
    outfilename = opts.gps_file.split('.')[0]+'_'+opts.trans+'trans.txt'
    trans_pol = opts.trans
else:
    outfilename = opts.gps_file
    trans_pol = 'none'

# Write header, transmitter, and column format info to outfile
with open(outfilename,'wb') as outfile:
    outfile.write(header+'\n')
    outfile.write('# Transmitter polarization: '+trans_pol+'\n')
    outfile.write('# Col Format: Time [GPS s], Lat [deg], Lon [deg], Alt [m]\n')

# Open tlog and get start_time
mlog = mavutil.mavlink_connection(opts.tlog)
start_time = Time(mlog.start_time,format='unix').gps
try: # Continuously write time + position to outfile until close
    while True:
        #loc = get_position(udp)
        pos = mlog.recv_match(type='GLOBAL_POSITION_INT',blocking=False)
        if not pos is None:
            sys.stdout.write('\r')
            sys.stdout.flush()
            byte_count = mlog.f.tell()
            timestamp = start_time + pos.time_boot_ms*TIME_SINCE_BOOT_FACTOR
            lat = pos.lat*1e-07
            lon = pos.lon*1e-07
            alt = pos.relative_alt*1e-03
            pos_str = '%.2f,%.5f,%.5f,%.5f' %(timestamp,lat,lon,alt)
            with open(outfilename,'ab') as outfile:
                outfile.write(pos_str+'\n')
            time.sleep(SLEEP_TIME)

        while pos:
            pos = mlog.recv_match(type='GLOBAL_POSITION_INT',blocking=False)
            if not pos is None:
                byte_count = mlog.f.tell()
                timestamp = start_time + pos.time_boot_ms*TIME_SINCE_BOOT_FACTOR
                lat = pos.lat*1e-07
                lon = pos.lon*1e-07
                alt = pos.relative_alt*1e-03
                pos_str = '%.2f,%.5f,%.5f,%.5f' %(timestamp,lat,lon,alt)
                with open(outfilename,'ab') as outfile:
                    outfile.write(pos_str+'\n')
                time.sleep(SLEEP_TIME)
        # Re-read tlog file and go to current byte location
        mlog.f.close()
        sys.stdout.write('Re-reading %s...\r' %opts.tlog)
        sys.stdout.flush()
        mlog = mavutil.mavlink_connection(opts.tlog)
        mlog.f.seek(byte_count)

except(KeyboardInterrupt):
    outfile.close()
    print '\n\n'+outfilename+' closed successfully'
    print 'Exiting...\n'
    sys.exit()
