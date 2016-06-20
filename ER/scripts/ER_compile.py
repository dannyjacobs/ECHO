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
import numpy as np
import sys,optparse
from scipy.interpolate import interp1d

r_earth = 6371000
secperweek = 604800

######################### Opts #############################

o = optparse.OptionParser()
o.set_description('Takes raw APM data and creates an interpolated, combined text file')
o.add_option('--trans',type=str,help='Polarization of Bicolog antenna onboard drone')
o.add_option('--width',type=int,default=1000,
        help='Width (number) of channels to keep in spectrum data')
o.add_option('--freq',type=float,default=137.500,
        help='Frequency to look for in data')
opts,args = o.parse_args(sys.argv[1:])


######################## Main ##########################
'''
# Check for valid transmitter polarization
cont = False
if opts.trans == 'NS' or opts.trans == 'EW':
    cont = True
if not cont:
    print "Please enter a valid transmitter polarization (NS or EW)\n"
    sys.exit()
'''
for infile in args:
    if 'spec' in infile:
        # Get Orbcomm files
        print "Spectrum File: %s" %infile
        lines = open(infile).readlines()
        SPEC_files = []
        for i,line in enumerate(lines):
            SPEC_files.append(line.rstrip('\n'))

        specTimes = []
        specData = []
        for SPEC_file in SPEC_files:
            lines = open(SPEC_file).readlines()
            for line in lines[1:-2]:
                string = line.strip(' \n')
                #if len(string.split(' ')) == 25:
                specTimes.append(float(string.split(',')[0]))
                specData.append(map(float,string.strip(' \n').split(',')[1:]))

        specData = np.array(specData)
        freqs = specData[0,:]
        freqIndex = np.where(np.abs(freqs-opts.freq).min()==np.abs(freqs-opts.freq))[0]
        freqs = freqs[freqIndex-opts.width:freqIndex+opts.width]
        specData = specData[1:,freqIndex-opts.width:freqIndex+opts.width]
        specTimes = Time(specTimes[1:],format='unix')
        print specTimes.gps.min(),specTimes.gps.max()

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
        weektimes = []
        isGPS = True
        startTime = 0
        for APM_file in APM_files:
            lines = open(APM_file).readlines()
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
                    if isGPS:
                        startTime = float(line.split(',')[-1])
                        isGPS = False

        weektimes = np.array(weektimes)
        GPSseconds = weektimes[:,1]*secperweek + weektimes[:,0]/1000.
        minAPM = GPSseconds.min()
        maxAPM = GPSseconds.max()
        print minAPM,maxAPM
        APM_times = Time(GPSseconds, format = 'gps')
        APM_lat,APM_lon,APM_alt = (np.array(APM_lat),np.array(APM_lon),
                    np.array(APM_alt))
        print APM_lat.shape,APM_lon.shape,APM_alt.shape
    else:
        print "\nPlease pass a valid APM and Orbcomm file.\n"
        sys.exit()

#Obtain minimum and maximum times for Interpolation
#Necessary to avoid interpolation range errors
minTime = minAPM; maxTime = maxAPM

#print specTimes[0].gps-APM_times[0].gps
#print specTimes[-1].gps-APM_times[-1].gps

print "Before time filter: ",specTimes.shape,specData.shape
#Obtain times from Orbcomm data that lie in the time range of the APM data
specIndices = np.where(np.logical_and(specTimes.gps>minTime,specTimes.gps<maxTime))[0]
specTimes,specData = (specTimes[specIndices],specData[specIndices])
print "After time filter: ",specTimes.shape,specData.shape


#Interpolation of APM_lat, APM_lon, and APM_alt to SH_times
from timeit import default_timer as timer
start = timer()
APM_lati = interp1d(APM_times.gps,APM_lat[:,0],kind='zero')
print specTimes[550].gps
print APM_lati(specTimes[550].gps)
end = timer()
print(end - start)
sys.exit()

APM_lati = APM_lati(specTimes.gps)
APM_loni= interp1d(APM_times.gps,APM_lon[:,0],kind='zero')
APM_loni = APM_loni(specTimes.gps)
APM_alti = interp1d(APM_times.gps,APM_alt[:,0],kind='zero')
APM_alti = APM_alti(specTimes.gps)

# Write to combined output file
outfileName = SPEC_file.split('_')[1:4]
outfile = open('_'.join(outfileName)+'_combined_cuts.txt','wb')
arg_strings = str(APM_files)+', '+str(SPEC_files)
outfile.write('# '+arg_strings+',start= '+specTimes[0].iso+',stop= '+
                      specTimes[-1].iso+'\n')
colheader = '# Index, Time (GPS s), Lat (deg), Long (deg), Rel Alt (m), Spectrum'
frequency_string = ','.join(map(str,freqs))
outfile.write(colheader+'\n'+frequency_string+'\n')
for i in range(0,len(specTimes)):
    spectrum_string = ','.join(map(str,specData[i,:]))
    outfile.write("%d,%s,%s,%s,%s,%s\n" % (i,specTimes.gps[i],APM_lati[i],APM_loni[i],APM_alti[i],spectrum_string))
outfile.close()
