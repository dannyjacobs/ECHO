from __future__ import absolute_import
import optparse,sys,threading,atexit
import numpy as np
from flask import Flask,jsonify
from .read_utils import get_data
from .position_utils import interp_pos
import time

# =========== Start Selection. These lines are copied from ECHO_server.py to fix this code.
o = optparse.OptionParser()
o.set_description('Reads in GPS positional data in realtime from a user specified \
text file. Starts a server which is queryable by a user on the same or another \
machine. The query returns an interpolated GPS position which can be read by the \
querier and used to accumulate GPS and spectral data into one output file.\
See ECHO_accumulate.py for the output file format.')

o.add_option('--gps_file',type=str,
    help='File name for GPS positional data to be read')
o.add_option('--dt',type=float,default=0.5,
    help='User specified time interval for binning resolution')
    #Since v_drone<2m/s, dt gives a maximum positional extrapolation range, i.e. dx~v*dt')
o.add_option('--host',type=str,default='10.1.1.1',
    help='Host address')

opts,args = o.parse_args(sys.argv[1:])



# Verify a GPS file was passed by the user
"""if not opts.gps_file:
    print('\n Please enter valid file for GPS information\nExiting...\n\n')
    sys.exit()"""
# ========= End Selection

''' NEED TO FIX THE CREATE_APP FUNCTION TO ACCOUNT FOR MODIFICATION OF GLOBAL QUANTITIES !!! '''
dataLock=threading.Lock()
pool_time=0.3

def create_app():
    app = Flask(__name__)

    def interrupt(): # Method called upon script exit
        global yourThread
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
                time.sleep(pool_time)
            elif currlen > lastlen:
                lastlen = currlen
                tmin,tmax = gps_raw[:,0].min(),gps_raw[:,0].max()
                # Create weights array for check of GPS data when user queries server
                counts,tbins = np.histogram(gps_raw[:,0],bins=int((tmax-tmin)/dt))
                #counts = list(counts)
                #counts.append(0) # len(counts) -1 = len(tbins)
                #weights = np.column_stack((counts,tbins))
        # Start the next thread
        yourThread = threading.Timer(pool_time, collection, ())
        yourThread.start()

    def initialize():
        # Do initialisation stuff here
        global yourThread
        # Create your thread
        yourThread = threading.Timer(pool_time, collection, ())
        yourThread.start()

    # Initiate
    initialize()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)

    # Add get function to app before returning
    @app.route('/ECHO/lms/v1.0/pos/<float:query_time>', methods=['GET'])
    def get_gps_pos(query_time,counts):
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

    # Return app with get function
    return app
