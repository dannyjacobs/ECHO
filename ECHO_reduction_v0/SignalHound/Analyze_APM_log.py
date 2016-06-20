import sys
import numpy as np
from astropy.time import Time

# Global variables
secperweek = 604800

#Extract APM data
def get_APMdata(filename):
    lines = open(filename).readlines()
    APM_lat = []
    APM_lon = []
    APM_alt =[]
    weektimes = []
    for line in lines:
        if line.startswith('GPS'):
            # Arducopter 3.2
            #APM_lat.append(map(float,line.split(',')[6:7]))
            #APM_lon.append(map(float,line.split(',')[7:8]))
            #APM_alt.append(map(float,line.split(',')[8:9]))
            #weektimes.append(map(float,line.split(',')[2:4])) #ms and week number

            # Arducopter 3.3
            APM_lat.append(map(float,line.split(',')[7:8]))
            APM_lon.append(map(float,line.split(',')[8:9]))
            APM_alt.append(map(float,line.split(',')[9:10]))
            weektimes.append(map(float,line.split(',')[3:5])) #ms and week number

    weektimes = n.array(weektimes)
    GPSseconds = weektimes[:,1]*secperweek + weektimes[:,0]/1000. #Convert number of weeks and ms into GPS seconds
    APM_times = Time(GPSseconds, format = 'gps')
    return APM_times, n.array(APM_lat), n.array(APM_lon), n.array(APM_alt)
    #APM_times as time object
    #APM_lat in degrees
    #APM_lon in degrees
    #APM_alt in meters

APM_file = sys.argv[1]

# Get APM data from file
APM_times, APM_lat, APM_lon, APM_alt = get_APMdata(APM_file)
print 'File:\t' + APM_file
print 'Start time:\t' + APM_times[0].iso
print 'Stop time:\t' + APM_times[-1].iso + '\n'
