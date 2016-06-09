#WAYPOINT RETURN

from astropy.time import Time
import numpy as np
import sys,optparse


o = optparse.OptionParser()
o.set_description('input a list of apm logs, outputs times corresponding to first and last waypoint command')
o.add_option('--first_waypoint',type=int,default=3,
    help='use this waypoint as the first starting point. sometimes its better to increase this to 3 or 4. [default=3]')
o.add_option('--waypts',action='store_true')
opts,args = o.parse_args(sys.argv[1:])

SECPERWEEK = 604800
LOG_SEC_PER_TICK = 1.e-6

##### FUNCTION TO RECORD TIMES:
def get_way(filename):
   lines=open(filename).readlines()
   GPS_weektimes,GPS_arm,CMD_time,CMD_num =[],[],[],[]
   for line in lines[626:]:
      if line.startswith('GPS'):
         GPS_weektimes.append(map(float,line.split(',')[3:5]))
         GPS_arm.append(float(line.split(',')[1]))
      if line.startswith('CMD'):
         CMD_time.append(float(line.split(',')[1].strip()))
         CMD_num.append(int(line.split(',')[3].strip()))
   GPS_weektimes = np.array(GPS_weektimes)
   GPS_seconds = GPS_weektimes[:,1]*SECPERWEEK + GPS_weektimes[:,0]/1000.
   GPS_arm= Time((np.array(GPS_arm[0])*LOG_SEC_PER_TICK), format = 'gps')
   GPS_time = Time(GPS_seconds, format='gps')
   CMD_time = (np.array(CMD_time).astype(float))*LOG_SEC_PER_TICK
   return GPS_time, GPS_arm, np.array(CMD_num), CMD_time

if opts.waypts:
    print '# waypoint times [all in gps seconds]'
else:
    print "#start stop length [all in gps seconds]"

i=0
for filename in args:
    f = open(filename, 'rb')
    lines=open(filename).readlines()
    i= i+1
    GPS_times, GPS_arm, CMD_num, CMD_times = get_way(filename)
    CMD_times = Time((CMD_times + (GPS_times.gps[0] - GPS_arm.gps)), format='gps')
    if opts.waypts:
        for i in range(1,CMD_times.shape[0]):
            print CMD_times[i].gps
    else:
        for p,CMD in enumerate(CMD_num):
            if CMD==opts.first_waypoint:
                print int(np.round((CMD_times.gps[p]),0)),
                start = int(np.round((CMD_times.gps[p]),0))
            if CMD==CMD_num.max():
                print int(np.ceil((CMD_times.gps[p]))),
                print int(np.ceil((CMD_times.gps[p]))) - start

#      print i-1, CMD_num[p].squeeze(), (CMD_time.gps[p]).squeeze(),CMD_time.iso[p]
