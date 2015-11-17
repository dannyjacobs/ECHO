'''

Author: Jacob Burba
Created: 08/14/15
Modified: 09/17/15

This script takes text files conatining APM and Orbcomm file names of interest and two options
specified by the user (--trans).  Please see the README file to see an example of a
valid text file that can be passed to the program.  The option passed by the user can be
defined as follows:

        --trans: Polarization of Bicolog antenna (N for NS polarization, E for EW polarization)

            ex: python orbcomm_compile.py orbFiles.txt apmFiles.txt --trans N

            - This command will create a combined data text file which corresponds to a
                Healpix run completed with a North/South Bicolog polarization throughout
                the duration of the flight.
            - The order of the inputs from the user are unimportant.  The files and parameter
                --trans can be passed by the user in any order.

An output file containing interpolated APM data and Orbcomm data will be created which
contains time, latitude, longitude, altitude, yaw, and orbcomm spectral data.  The column
ordering and all input files used in the creation of the compiled file can be found in the first
three lines of the file.

'''

from astropy.time import Time
import datetime as date
import numpy as n
import exifread
import sys,optparse
import os
from pylab import *
from scipy.interpolate import interp1d
import fileinput
import matplotlib.pyplot as plt

r_earth = 6371000
secperweek = 604800

######################### Opts #############################

o = optparse.OptionParser()
o.set_description('Takes raw APM/Orbcomm data and creates an interpolated, combined text file')
o.add_option('--trans',type=str,help='Polarization of Bicolog antenna onboard drone')
opts,args = o.parse_args(sys.argv[1:])


######################## Main ##########################

# Check for valid transmitter polarization
cont = False
if opts.trans == 'NS' or opts.trans == 'EW':
    cont = True
if not cont:
    print "Please enter a valid transmitter polarization (NS or EW)\n"
    sys.exit()

for infile in args:
    if 'orb' in infile:
        # Get Orbcomm files
        print "Orbcomm File: %s" %infile
        lines = open(infile).readlines()
        ORB_files = []
        for i,line in enumerate(lines):
            ORB_files.append(line)
            ORB_files[-1] = ORB_files[-1].strip(' \n')

        orbTimes = []
        orbData = []
        for ORB_file in ORB_files:
            lines = open(ORB_file).readlines()
            for line in lines:
                string = line.strip(' \n')
                if len(string.split(' ')) == 25:
                    orbTimes.append(float(string.split()[0]))
                    orbData.append(map(float,string.strip(' \n').split()[1:]))

        orbData = n.array(orbData)
        orbTimes = Time(orbTimes,format='gps')
    elif 'apm' in infile:
        # Get APM data
        print "APM File: %s" %infile
        listFiles = open(infile).readlines()
        APM_files = []
        for i,line in enumerate(listFiles):
            APM_files.append(line)
            APM_files[i] = APM_files[i].strip('\n')

        # Process APM data\
        APM_lat = []
        APM_lon = []
        APM_alt =[]
        ATT_yaw=[]
        weektimes = []
        ATT_times=[]
        isGPS = True
        startTime = 0
        for APM_file in APM_files:
            lines = open(APM_file).readlines()
            for line in lines:
                if line.startswith('GPS'):
                    APM_lat.append(map(float,line.split(',')[6:7]))
                    APM_lon.append(map(float,line.split(',')[7:8]))
                    APM_alt.append(map(float,line.split(',')[8:9]))
                    weektimes.append(map(float,line.split(',')[2:4])) #ms and week number
                    if isGPS:
                        startTime = float(line.split(',')[-1])
                        isGPS = False
                if line.startswith('ATT'):
                    ATT_times.append(map(float,[line.split(',')[1].strip(' ')]))
                    ATT_yaw.append(map(float,[line.split(',')[6].strip(' ')]))

        weektimes = n.array(weektimes)
        ATT_times = n.array(ATT_times)
        GPSseconds = weektimes[:,1]*secperweek + weektimes[:,0]/1000.
        ATTGPSseconds = ATT_times/1000.+GPSseconds[0]-startTime/1000.
        minAPM = GPSseconds.min()
        maxAPM = GPSseconds.max()
        APM_times = Time(GPSseconds, format = 'gps')
        ATT_times = Time(ATTGPSseconds, format = 'gps')
        APM_lat,APM_lon,APM_alt,ATT_yaw = (n.array(APM_lat),n.array(APM_lon),
                    n.array(APM_alt),n.array(ATT_yaw))
    else:
        print "\nPlease pass a valid APM and Orbcomm file.\n"
        sys.exit()

#Obtain minimum and maximum times for Interpolation
#Necessary to avoid interpolation range errors
minTime = n.max([minAPM,ATT_times.gps[0]])
maxTime = n.min([maxAPM,ATT_times.gps[-1]])

#Obtain times from Orbcomm data that lie in the time range of the APM data
orbIndices = n.where(n.logical_and(orbTimes.gps>minTime,orbTimes.gps<maxTime))[0]
orbTimes,orbData = (orbTimes[orbIndices],orbData[orbIndices])

#Interpolation of APM_lat, APM_lon, and APM_alt to SH_times
APM_lati = interp1d(APM_times.gps,APM_lat[:,0],kind='zero')
APM_lati = APM_lati(orbTimes.gps)
APM_loni= interp1d(APM_times.gps,APM_lon[:,0],kind='zero')
APM_loni = APM_loni(orbTimes.gps)
APM_alti = interp1d(APM_times.gps,APM_alt[:,0],kind='zero')
APM_alti = APM_alti(orbTimes.gps)
ATT_yawi = interp1d(ATT_times.gps[:,0],ATT_yaw[:,0],kind='zero')
ATT_yawi = ATT_yawi(orbTimes.gps)

# Write to combined output file
outfileName = APM_file.split('_')
outfile = open(outfileName[1]+'_combined_'+opts.trans+'transmitter.txt','wb')
arg_strings = str(APM_files)+', '+str(ORB_files)
outfile.write('# '+arg_strings+',start='+str(orbTimes.gps[0])+',stop='+
                      str(orbTimes.gps[-1])+'\n')
colheader = '# Index, Time (GPS s), Lat (deg), Long (deg), Rel Alt (m), Yaw (deg), Spectrum'
specInfo = '# Spectrum info (ant-dipole): S-NS[7:12], N-NS[13:18], S-EW[14:19], N-EW[20:25]'
outfile.write(colheader+'\n'+specInfo+'\n')
for i in range(0,len(orbTimes)):
    spectrum_string = ','.join(map(str,orbData[i,:]))
    outfile.write("%d,%s,%s,%s,%s,%s,%s\n" % (i,orbTimes[i],APM_lati[i],APM_loni[i],APM_alti[i],ATT_yawi[i],spectrum_string))
outfile.close()
