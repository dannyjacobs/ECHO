'''
    Author: Jacob Burba
'''

import sys,os,optparse
import time
import numpy as np
from pymavlink import mavutil

o = optparse.OptionParser()
o.set_description('Takes raw APM/Orbcomm data and creates an interpolated, combined text file')
o.add_option('--gps_file',type=str,help='File name for output of GPS data')
#o.add_option('--trans',type=str,help='Transmitting antenna polarization')
opts,args = o.parse_args(sys.argv[1:])


# Establish connection with Drone via UDP
udp = mavutil.mavudp('127.0.0.1:14551')
dt = 0.2 # time delay between GPS messages
outfile = open(opts.gps_file,'wb') # Open output file for writing
date = time.strftime('%m_%d_%Y')
currtime = time.strftime('%H:%M:%S') # 24 Hr format
header = '# GPS Positions file for '+date+', '+currtime
outfile.write(header+'\n')
outfile.write('# Col Format: Lat [deg], Lon [deg], Rel_alt [m]\n')

try:
    while True:
        loc = udp.location()
        if loc:
            loc_str = '%.5f\t%.5f\t%.5f' %(loc.lat,loc.lng,loc.alt)
            outfile.write(loc_str+'\n')
        else:
            print 'No New GPS point.  Sleeping for %.1f s...' %dt
            time.sleep(dt)

except KeyboardInterrupt:
    outfile.close()
    print '\n\n'+opts.gps_file+' closed successfully'
    print 'Exiting...\n'
    sys.exit()
