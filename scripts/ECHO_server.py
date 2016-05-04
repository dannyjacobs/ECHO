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

def get_gps():
    gps_raw = []
    lines = open(opts.gps_file).readlines()
    count = len(lines)
    gps_raw = [map(float,line.split(',')) for line in lines[2:] if len(line.split(','))==4]
    return np.array(gps_raw)
# end get_gps


def interp(gps):
    lati = interp1d(gps[:,0],gps[:,1],kind='zero')
    loni = interp1d(gps[:,0],gps[:,2],kind='zero')
    alti = interp1d(gps[:,0],gps[:,3],kind='zero')
    return lati,loni,alti
# end interp


def create_app():
    app = Flask(__name__)

    def interrupt(): # Method called upon script exit
        global yourThread
        if __name__ == yourThread.getName():
            with open(logfilestr,'ab') as logfile:
                logfile.write(strftime('%H:%M:%S')+' - '+yourThread.name()+' closed '+'\n')
        # Close active thread
        yourThread.cancel()

    def collection():
        # Call global variables that will be used/modified
        global gps_raw,lati,loni,alti
        global lastlen,logfilestr
        global tmin,tmax,dt
        global counts,tbins,weights
        global yourThread
        with dataLock: # Wait for lock on current thread
            gps_raw = get_gps()
            lati,loni,alti = interp(gps_raw)
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
            else:
                if __name__=='__main__':
                    print 'Error retreiving GPS data'
        # Set the next thread to happen
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
# end create_app


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
