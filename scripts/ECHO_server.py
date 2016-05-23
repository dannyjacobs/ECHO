'''

    Author: Jacob Burba

    ECHO_server.py initiates a queriable Flask server that contains GPS positions for the drone.
    The GPS information is read in from the user specified output file from ECHO_GET_GPS.py
    and then broadcast via 10.1.1.1:5000, where the port 5000 is the default port for Flask.
    The user can specify a custom IP address and port number, if desired.  A secondary machine,
    used to obtain radio spectra from the Signal Hound, connected via ethernet/wifi can then
    query this server server with the time at which a spectrum is read.  The server then returns
    an interpolated GPS position at the query time, if available, or an error message saying
    that the query time lies outside the range of available GPS position data.  An example call
    can be seen as follows

                        python ECHO_server.py --gps_file <output_filename>

    The user does not need to pass the flags --dt and --host, as they have default values of
    0.5 and 10.1.1.1, respectively.  They can be set to a custom value by issuing the flags
    such as in the following example

        python ECHO_server.py --gps_file <output_filename> --dt 0.3 --host 10.13.22.1


    NOTE: Due to the structure of the Flask app, the user must exit the code by executing
    CTRL + C twice, once to end the Flask app, and one to end the Python program.

'''

import threading,atexit
import optparse,sys
import numpy as np
from scipy.interpolate import interp1d
from flask import Flask,jsonify
from time import sleep,strftime
from astropy.time import Time

o = optparse.OptionParser()
o.set_description('Reads in GPS positional data in realtime from a user specified text file.\
    Starts a server which is queryable by a user on the same or another machine.\
    The query returns an interpolated GPS position which can be read by the querier\
    and used to accumulate GPS and spectral data into one output file.\
    See ECHO_accumulate.py for the output file format.')
o.add_option('--gps_file',type=str,
    help='File name for GPS positional data to be read')
o.add_option('--dt',type=float,default=0.5,
    help='User specified time interval for binning resolution.\
    Since v_drone<2m/s, dt gives a maximum positional extrapolation range, i.e. dx~v*dt')
o.add_option('--host',type=str,help='Host address')
opts,args = o.parse_args(sys.argv[1:])

# Reading functions
def get_data(infile,filetype=None,freqs=[],freq_chan=None):
    if filetype == 'gps':
        '''
            Read in GPS position file.
            The first line contains start date/time information for file.
            The second line contains the column formatting:
                0 Time [GPS s], 1 Lat [deg], 2 Lon [deg], 3 Alt [m]
        '''
        gps_arr = []
        lines = open(infile).readlines()
        count = len(lines)
        gps_arr = [map(float,line.rstrip('\n').split(',')) for line in lines[2:] if len(line.split(','))==4]
        return np.array(gps_arr)

    elif filetype == 'sh':
        '''
            Read in Signal Hound file.
            The first line contains a comment and is not needed.
            The second line contains a list of all frequency bins read by the Signal Hound.
            Column format for subsequent lines is:
                0 Time [unix sec], 1: Spectrum [dB]
        '''
        spec_times = []
        spec_raw = []
        lines = open(infile).readlines()
        count = len(lines)
        if count != 0:
            if len(freqs) == 0:
                freqs = np.array(map(float,lines[1].rstrip('\n').split(',')[1:]))
                freq_chan = np.argmax(freqs == opts.freq) # Get index of opts.freq for gridding
                freqs = freqs[freq_chan-10:freq_chan+10] # opts.freq is freqs[10]
            for line in lines:
                if line.startswith('#'):
                    continue
                line = line.rstrip('\n').split(',')
                if len(line) == 4097: # Make sure line has finished printing
                    spec_times.append(float(line[0]))
                    spec_raw.append(map(float,line[freq_chan-10:freq_chan+10]))
        return np.array(spec_times),np.array(spec_raw),np.array(freqs),freq_chan

    elif filetype == 'echo':
        '''
            Read in ECHO file.
            The first two lines contain comment and formatting information.
            Third line contains lat0 and lon0 of antenna under test.
            Column format for subsequent lines is:
                0 Time [gps sec], 1 Lat [deg], 2 Lon [deg], 3 Alt [m], 4: Spectrum [dB]
        '''
        all_Data = []
        freqs = []
        #print '\nReading in %s...' %inFile
        lines = open(infile).readlines()
        # Add information from flight to all_Data array
        if not 'transmitter' in infile:
            lat0,lon0 = map(float,lines[2].rstrip('\n').split(':')[1].strip(' ').split(','))
            freqs = map(float,lines[3].rstrip('\n').split(':')[1].strip(' ').split(','))
            freqs = np.array(freqs)
        for line in lines[4:]: # Data begins on fifth line of accumulated file
            if line.startswith('#'):
                continue
            elif not line.split(',')[1] == '-1':
                    all_Data.append(map(float,line.rstrip('\n').split(',')))
        all_Data = np.array(all_Data)
        #print 'Converted to array with shape %s and type %s' %(all_Data.shape,all_Data.dtype)
        # Extract information from all_Data array
        if 'transmitter' in infile: # Green Bank data
            spec_times,lats,lons,alts = (all_Data[:,1],all_Data[:,2],all_Data[:,3],all_Data[:,4])
            if 'Nant' in infile:
                lat0,lon0 = (38.4248532,-79.8503723)
                if 'NS' in infile:
                    spec_raw = all_Data[:,12:17] # N antenna, NS dipole
                if 'EW' in infile:
                    spec_raw = all_Data[:,24:29] # N antenna, EW dipole
            if 'Sant' in infile:
                lat0,lon0 = (38.4239235,-79.8503418)
                if 'NS' in infile:
                    spec_raw = all_Data[:,6:11] # S antenna, NS dipole
                if 'EW' in infile:
                    spec_raw = all_Data[:,18:23] # S antenna, EW dipole
        else:
            spec_times,lats,lons,alts,spec_raw = (all_Data[:,0],all_Data[:,1],all_Data[:,2],\
                                                                        all_Data[:,3],all_Data[:,4:])
        return spec_times,spec_raw,freqs,lats,lons,alts,lat0,lon0

    else:
        print '\nNo valid filetype found for %s' %infile
        print 'Exiting...\n\n'
        sys.exit()


# Time functions


# Position functions
def interp_pos(gps):
    lati = interp1d(gps[:,0],gps[:,1],kind='zero')
    loni = interp1d(gps[:,0],gps[:,2],kind='zero')
    alti = interp1d(gps[:,0],gps[:,3],kind='zero')
    return lati,loni,alti


# Server API functions
def create_app():
    app = Flask(__name__)
    def interrupt(): # Method called upon script exit
        global yourThread
        #if __name__ == yourThread.getName():
        #    with open(logfilestr,'ab') as logfile:
        #        logfile.write(strftime('%H:%M:%S')+' - '+yourThread.name()+' closed '+'\n')
        # Close active thread
        yourThread.cancel()
    def collection():
        # Call global variables that will be used/modified
        global gps_raw,lati,loni,alti
        global lastlen
        global tmin,tmax,dt
        global counts,tbins,weights
        global yourThread
        with dataLock: # Wait for lock on current thread
            gps_raw = get_data(opts.gps_file,filetype='gps')
            lati,loni,alti = interp_pos(gps_raw)
            currlen = gps_raw.shape[0]
            if currlen == lastlen:
                sleep(POOL_TIME)
            elif currlen > lastlen:
                lastlen = currlen
                tmin,tmax = gps_raw[:,0].min(),gps_raw[:,0].max()
                # Create weights array for check of GPS data when user queries server
                counts,tbins = np.histogram(gps_raw[:,0],bins=int((tmax-tmin)/dt))
                counts = list(counts)
                counts.append(0) # len(counts) -1 = len(tbins)
                weights = np.column_stack((counts,tbins))
            #else:
            #    if __name__=='__main__':
            #        print 'Error retreiving GPS data'
        # Start the next thread
        yourThread = threading.Timer(POOL_TIME, collection, ())
        yourThread.start()
    def initialize():
        # Do initialisation stuff here
        global yourThread
        # Create your thread
        yourThread = threading.Timer(POOL_TIME, collection, ())
        yourThread.start()
    # Initiate
    initialize()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
    return app


# Plotting functions


'''##############################
                                    MAIN
##############################'''

if not opts.gps_file: # Verify a GPS file was passed by the user
    print '\n Please enter valid file for GPS information\nExiting...\n\n'
    sys.exit()

POOL_TIME = 0.3 # Seconds between thread creation/execution

# Global variables
gps_raw = get_gps()
lati,loni,alti = interp(gps_raw)

# Get current number of GPS data points for monitoring of opts.gps_file
lastlen = gps_raw.shape[0]
tmin,tmax = gps_raw[:,0].min(),gps_raw[:,0].max()

# Create weights array for check of GPS data when user queries server
dt = opts.dt
counts,tbins = np.histogram(gps_raw[:,0],bins=int((tmax-tmin)/dt))
counts = list(counts)
counts.append(0)
weights = np.column_stack((counts,tbins))

# Create Lock object to access variables on an individual thread
# https://docs.python.org/2/library/threading.html#lock-objects
dataLock = threading.Lock()

# Thread handler
yourThread = threading.Thread()

# Initiate app
app = create_app()
# Assign and create get function for server
@app.route('/ECHO/lms/v1.0/pos/<float:query_time>', methods=['GET'])
def get_gps_pos(query_time):
    if np.logical_and(query_time>=gps_raw[0,0],query_time<=gps_raw[-1,0]):
        if counts[np.abs(tbins-query_time).argmin()] > 0:
            # Return a dictionary of latitude, longitude, and altitude at query time
            lat,lon,alt = float(lati(query_time)),float(loni(query_time)),float(alti(query_time))
            pos = {'lat': lat, 'lon': lon, 'alt': alt}
            return jsonify(pos)
        else:
            pos = {'lat': -1, 'lon': -1, 'alt': -1}
            return jsonify(pos)
    else:
        return 'Error: Query time '+str(query_time)+' outside range '+\
                    str(gps_raw[0,0])+'to'+str(gps_raw[-1,0])
# Run server app
if opts.host:
    app.run(debug=True,host=opts.host,port=5000)
else:
    app.run(debug=True,host='10.1.1.1',port=5000)
