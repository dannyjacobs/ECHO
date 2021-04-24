from __future__ import print_function
from __future__ import absolute_import
import numpy as np,healpy as hp
import sys
import glob
from astropy.time import Time

from scipy.interpolate import interp1d
from .time_utils import flight_time_filter,waypt_time_filter, DatetimetoUnix
from distutils.version import StrictVersion
import pyulog.core as pyu
import pyulog.ulog2csv as pyucsv
from pyuvdata import UVBeam
from pyuvdata.data import DATA_PATH
import h5py
import os
import pandas as pd

SEC_PER_WEEK = 604800
APMLOG_SEC_PER_TICK = 1.0e-6
def dB(x):
    return 10*np.log10(x)
def dB2(x): #this is the definition of dB for Voltages
    return 20*np.log10(x)

def concat_times(Ts):
    "input a list of astropy time vectors"
    "return a single concatenated time vector"
    return Time(np.concatenate([t.gps for t in Ts]),format='gps')

def read_map(filename):
    M = np.ma.array(hp.read_map(filename),fill_value=hp.UNSEEN)
    M = np.ma.masked_where(hp.UNSEEN==M,M)
    M.fill_value = hp.UNSEEN
    return M

def write_map(filename,M):
    "write out a masked healpix map with the correct fill values"
    M.set_fill_value(hp.UNSEEN)
    hp.write_map(filename,M.filled())
    return 0


def channel_select(freqs,rxspectrum,channel):
    """
    input:
        freqs: measured frequences in MHz
        rxspectrum: power in volt^2 shape(len(times),len(freqs))
        channel: give a channel as an int or a float frequency in MHz

    return:
        a single vector ntimes long

    """
    if type(channel)==int:
        if channel>len(freqs):
            print(("error: channel",channel))
            print(("not found in input freqs vector of length",len(freqs)))
            return None
        mychan=channel
    elif type(channel)==float:
        if channel>freqs.max() or channel<freqs.min():
            print(("error: selected freq",channel))
            print(("not found in input freqs vector spanning",freqs.min(),freqs.max()))
            return None
        mychan = np.abs(freqs-channel).argmin()
    return rxspectrum[:,mychan]

def interp_rx(postimes,rxtimes,rx):
    """
    input:
        postimes: astropy.Time.Time vector (output points)
        rxtime: astropy.time.Time vector (input points)
        Assumes that both position and spectrum data have been properly flagged
        and that the flags match between the two

    return:
        interpolation of the rx power to the gps times
    Note: this is just a general interpolation function that uses astropy times
       and can be used for anything

    """
    power_interp_model = interp1d(rxtimes.gps,rx, bounds_error=False)
    rx_interp = power_interp_model(postimes.gps)
    return rx_interp

def flag_angles(angletimes,angles,sigma=2):
    """
    input:
        angletimes:astropy.time.Time vector
        angles: (1,len(angletimes))

        sigma: flag values more than this many sigmas above the mean

    return:
        mask
        times during which angles are bad
    """
    #generate a list of bad angletimes

    yawcos = np.cos(angles[0]*np.pi/180)
    mean_yawcos = np.mean(yawcos)
    if mean_yawcos>0.5:
        yawcos = np.sin(angles[0]*np.pi/180) #branch cut issues!
        mean_yawcos = np.mean(yawcos)
    std_yawcos = np.std(yawcos)
    yawmask = np.abs(yawcos-mean_yawcos)/std_yawcos>sigma
    badyaw_indices = np.where(yawmask)[0]
    return yawmask,angletimes[badyaw_indices]

def apply_flagtimes(datatimes,flagtimes,dt):
    #generate a mask for postimes (astropy.time.Time)
    #given a list of times which are bad (astropy.time.Time)
    #flag anything within dt seconds (float seconds)
    mask = np.zeros(len(datatimes))
    for t in flagtimes.gps:
        bad_ind = np.where(np.logical_and(
                        datatimes.gps>(t-dt),
                        datatimes.gps<(t+dt)))
        mask[bad_ind] = 1
    return mask
def flag_waypoints(postimes,waypoint_times):
    """
    input:
        postimes: astropy.time.Time vector matching GPS solutions
        waypoint_times: astropy.time.Time entries matching times reached wypts

    return:
        flags on the postimes time base (ie matching len(postimes))
    """
    return np.zeros(len(postimes))

def mission_endpoint_flagging(pos_data,wpt_data):
    """Read in position and waypoint array, flag mission endpoints and return valid mission data.

    Args:
        pos_data: the ulog to be converted.
        wpt_data:

    Returns:
        flagged_data: array of flagged data.
        mission_data: array of valid mission data.

    """
    flagged_indices = []
    mission_indices = []
    mission_start = 0
    mission_end = wpt_data[-1][0]

    for row in wpt_data:
        if row[1] == 1:
            mission_start = row[0]
            break

    for index,row in enumerate(pos_data):
        if row[0]<mission_start or row[0]>mission_end: flagged_indices.append(index)
        else: mission_indices.append(index)

    flagged_data = np.delete(pos_data,mission_indices,0)
    mission_data = np.delete(pos_data,flagged_indices,0)
    return flagged_data, mission_data


def read_tlog_txt(tlog):
    """Read in text files converted from tlogs, put them into appropriate arrays.

    Args:
        tlog (int): the text tlog to be read.

    Returns:
        wpt_array: waypoints.
        global_array: global position.
        local_array: local position.
        gps_array: gps raw data.
    """
    wpt_data = []
    global_data = []
    local_data = []
    gps_data = []
    #att_data = []

    lines = open(tlog).readlines()
    for line in lines:

        if line.find('mavlink_mission_item_reached_t') != -1:
            datapoints = line.split()
            if datapoints[11]=='mavlink_mission_item_reached_t':
                wpt_data.append([datapoints[0]+' '+datapoints[1]+' '+datapoints[2],datapoints[13]])
        elif line.find('mavlink_global_position_int_t') != -1:
            datapoints = line.split()
            if datapoints[15]!='time_boot_ms':
                global_data.append([datapoints[0]+' '+datapoints[1]+' '+datapoints[2],float(datapoints[13])/1e3,float(datapoints[15])/1e7,float(datapoints[17])/1e7,(float(datapoints[19])/1e3)-1477.8,float(datapoints[29])/1e2])
        elif line.find('mavlink_local_position_ned_t') != -1:
            datapoints = line.split()
            if datapoints[15]!='time_boot_ms':
                local_data.append([datapoints[0]+' '+datapoints[1]+' '+datapoints[2],float(datapoints[13])/1e3,datapoints[15],datapoints[17],float(datapoints[19])*-1])
        elif line.find('mavlink_gps_raw_int_t') !=- 1:
            datapoints = line.split()
            if datapoints[15]!='time_usec':
                gps_data.append([datapoints[0]+' '+datapoints[1]+' '+datapoints[2],float(datapoints[13])/1e6,float(datapoints[15])/1e7,float(datapoints[17])/1e7,float(datapoints[19])/1e3])
        #elif line.find('mavlink_attitude_t') != -1:
            #datapoints = line.split()
            #if datapoints[15]!='body_roll_rate' and datapoints[15]!='time_boot_ms': att_data.append([datapoints[1],datapoints[13],datapoints[15],datapoints[17],datapoints[19]])

    wpt_data = DatetimetoUnix(wpt_data)
    global_data = DatetimetoUnix(global_data)
    local_data = DatetimetoUnix(local_data)
    gps_data = DatetimetoUnix(gps_data)
    #DatetimetoUnix(att_data)

    wpt_array = np.array(wpt_data,dtype='int')
    global_array = np.array(global_data,dtype='float')
    local_array = np.array(local_data,dtype='float')
    gps_array = np.array(gps_data,dtype='float')
    #att_array = np.array(att_data)
    return wpt_array, global_array, local_array, gps_array#, att_array

def read_ulog(ulog, output=None, messages='vehicle_global_position,vehicle_local_position,vehicle_gps_position'):
    """Read in ulog file, put them into appropriate arrays, then save to .csv

    Input:
        ulog (int): the ulog to be converted.

    Output:
        global_array: global position.
        local_array: local position.
        gps_array: gps raw data.
    """
    name = ulog[:-4]
    if output:
        pyucsv.convert_ulog2csv(ulog,messages=messages, output=output ,delimiter=',')

        global_data = np.genfromtxt(name+'_vehicle_global_position_0.csv', delimiter=',',skip_header=1,usecols=(0,1,2,3,9))
        global_data[:,0] = global_data[:,0]/1e6
        global_data[:,3] = global_data[:,3]-1477.8

        local_data = np.genfromtxt(name+'_vehicle_local_position_0.csv', delimiter=',',skip_header=1,usecols=(0,1,2,3,4,5,6,20,21))
        local_data[:,0] = local_data[:,0]/1e6
        local_data[:,6] = local_data[:,6]*-1

        gps_data = np.genfromtxt(name+'_vehicle_gps_position_0.csv', delimiter=',',skip_header=1,usecols=(0,1,2,3,4))
        gps_data[:,0] = gps_data[:,0]/1e6
        gps_data[:,1] = gps_data[:,1]/1e6
        gps_data[:,2] = gps_data[:,2]/1e7
        gps_data[:,3] = gps_data[:,3]/1e7
        gps_data[:,4] = gps_data[:,4]/1e3
    else:
        msg_filter = messages.split(',') if messages else None
        log=pyu.ULog(ulog, message_name_filter_list=msg_filter)
        biglist=[]
        for data in log.data_list:
            data_keys = [f.field_name for f in data.field_data]
            data_keys.remove('timestamp')
            data_keys.insert(0, 'timestamp')
            datalist=[]
            for i in range(len(data.data['timestamp'])):
                rowlist=[]
                for k in range(len(data_keys)):
                    rowlist.append(data.data[data_keys[k]][i])
                datalist.append(rowlist)
            biglist.append((str(data.name),np.asarray(datalist, dtype=float)))

        for i,mess in enumerate(msg_filter):
            if "global" in biglist[i][0]:
                global_data = biglist[i][1][:,[0,1,2,3,9]]
            if "local" in biglist[i][0]:
                local_data = biglist[i][1][:,[0,1,2,3,4,5,6,20,21]]
            if "gps" in biglist[i][0]:
                gps_data = biglist[i][1][:,[0,1,2,3,4]]

        global_data[:,0] = global_data[:,0]/1e6
        global_data[:,3] = global_data[:,3]-1477.8

        local_data[:,0] = local_data[:,0]/1e6
        local_data[:,6] = local_data[:,6]*-1

        gps_data[:,0] = gps_data[:,0]/1e6
        gps_data[:,1] = gps_data[:,1]/1e6
        gps_data[:,2] = gps_data[:,2]/1e7
        gps_data[:,3] = gps_data[:,3]/1e7
        gps_data[:,4] = gps_data[:,4]/1e3

        #u_log_dict = {'global_position_u':,'local_position_u':,'gps_position_u':gps_data}
    return global_data, local_data, gps_data

def read_h5(dataFile):
    """
    Read in receiver data file, put them into appropriate arrays

    Input:
        target_data (HDF5 data file): the datafile for the received power for the target antenna, saved in in h5 format.

    Output:
        dataDict: A dictionary containing the observation data. Includes observations, tunings, times, XX and YY polarizations, frequencies
    """

    target_data = h5py.File(dataFile,'r')
    keys = [key for key in target_data.keys()]
    #obs_keys = [obsKey for key in keys]
    dataDict = {}
    for key in keys:
        obsKeys = [obsKey for obsKey in target_data[key].keys()]
        obsDict = {}
        for obsKey in obsKeys:
            if obsKey == 'time':
                obsDict[obsKey] = np.asarray(target_data[key][obsKey])
            if obsKey != 'time':
                tuningKeys = [tunKey for tunKey in target_data[key][obsKey].keys()]
                tunDict = {}
                dataKeys = []
                for tunKey in tuningKeys:
                    #print(key, obsKey, tunKey)
                    data = np.asarray(target_data[key][obsKey][tunKey])
                    tunDict[tunKey] = data
                obsDict[obsKey] = tunDict
        dataDict[key] = obsDict
    return dataDict

def CST_to_hp(beamfile,outfile,nside=8,rot=0,zflip=False):
    '''
    Reads in a ASCII formatted CST export file and returns a healpix map.
    Also saves a .fits file to the current directory.
    This function is an adaptation of CST_to_healpix.py in the ECHO github.
    beamfile = CST export file
    outfile = name of the generated fits file, string
    nside = number of sides per healpix pixel, must be 2^n int, 8 is typical
    rot = rotates around the pole by 90deg*rot
    zflip = inverts the Z axis
    '''

    raw_data = np.loadtxt(beamfile,skiprows=2,usecols=(0,1,2))
    thetas = raw_data[:,0]*np.pi/180 #radians
    phis = raw_data[:,1]*np.pi/180 #radians
    gain = raw_data[:,2]
    #account for stupid CST full circle cuts
    phis[thetas<0] += np.pi
    thetas[thetas<0] = np.abs(thetas[thetas<0])

    phis += rot*(np.pi/2)
    if zflip==True: thetas = np.pi - thetas

    hp_indices = hp.ang2pix(nside,thetas,phis)
    hp_map = np.zeros(hp.nside2npix(nside))
    hp_map[hp_indices] = gain
    hp_map -= hp_map.max()
    hp.write_map(outfile,hp_map,fits_IDL=False,overwrite=True)
    return hp_map

def read_CST_puv(CST_txtfile, beam_type, frequency, telescope_name, feed_name, feed_version, model_name, model_version, feed_pol):
    '''
    Reads in a ASCII formatted CST export file and returns a beam model using pyuvbeam.

    Inputs:
        CST_txtfile: CST export file
        beam_type (str): efield or power
        frequency (list, Hz): our reference frequency
        telescope_name (str): The instrument name
        feed_name (str): The name of the feed
        feed_version (str): The version of the feed
        model_name (str): Name for the model
        model_version (str): version of the model
        feed_pol (str): polarization of the feed ('x','y','xx','yy')
    '''
    beam = UVBeam()
    beam.read_cst_beam(CST_txtfile, beam_type=beam_type, frequency=frequency,
                   telescope_name=telescope_name, feed_name=feed_name, feed_version=feed_version,
                   model_name = model_name, model_version=model_version, feed_pol=feed_pol)
    return beam

def read_cst_efield_slice(cstfile):
    h5_exts = ['.h5, .hdf5']
    req_keys = ['E-Field', 'Position']
    file_name, file_ext = os.path.splitext(cstfile)
    efield = None
    if file_ext=='.txt':
        #stuff here
        print('txtfile')
    elif file_ext in h5_exts:
        slice_obj = h5py.File(cstfile, 'r')
        for key in req_keys:
            if key not in slice_obj.keys():
                print('{0} key not found in file.'.format(key))
                return efield
        efield_l=np.zeros(slice_obj['Position'].shape[0])
        zfield=[]
        x_arr = np.zeros(slice_obj['Position'].shape[0])
        y_arr = np.zeros(slice_obj['Position'].shape[0])
        z_arr = np.zeros(slice_obj['Position'].shape[0])

        for i,field in enumerate(fa['E-Field'][:]):
            x = slice_obj['x']['re']+field['x']['im']*1j
            y = slice_obj['y']['re']+field['y']['im']*1j
            z = slice_obj['z']['re']+field['z']['im']*1j
            e_amp=np.sqrt(np.abs(x)**2 + np.abs(y)**2 + np.abs(z)**2)
            efield_l[i] = e_amp
            x_arr[i] = np.abs(x)
            y_arr[i] = np.abs(y)
            z_arr[i] = np.abs(z)
        eshape = efield_l.reshape((10,10))
        xshape = x_arr.reshape((10,10))
        yshape =  y_arr.reshape((10,10))
        zshape =  z_arr.reshape((10,10))

        x_pos, y_pos, z_pos = np.zeros(100),np.zeros(100),np.zeros(100)
        fig=plt.figure(facecolor='w')
        ax=fig.add_subplot(111,projection='3d')
        for i,(xpos,ypos,zpos) in enumerate(fa['Position']):
            x_pos[i] = xpos
            y_pos[i] = ypos
            z_pos[i] = zpos
    return eshape

def read_csv(filename):
    """
    Read in receiver data file, put them into appropriate arrays.

    Input:
        :filename (HDF5 data file): the datafile for the fieldfox, saved in CSV format.

    Output:
        dataDict: A dictionary containing the observation data. Includes observations, tunings, times, XX and YY polarizations, frequencies
    """
    #find trace line
    file=open(filename)
    flag=0
    index=0
    while True:
        line = file.readline()
        index += 1
        if 'Trace #' in line:
            flag=1
            break
        if not line:
            break
    if flag==0:
        print('No Trace header found')
        break
    #skip to line above trace line
    header_idx=index-2
    #read in csv as dataframe
    data=pd.read_csv(filename, skiprows=header_idx)
    #edit column names to use proper headers on the next line, copies freqs from line above
    for i in range(5):
        data.rename(columns={data.columns[i]:data.iloc[0,i]}, inplace=True)
    #remove first erroneous line containing headers
    data.drop([0], inplace=True)
    data.drop([data.shape[0]], inplace=True)
    #convert times to unix
    months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    datetime_txt=data.iloc[:,1].values
    times=[]
    for i,row in enumerate(datetime_txt):
        mon=months.index(row[0:3])
        if row[25:14] == 'PM' and row[12:14]<12:
            hr = 12 + int(row[12:14])
        else:
            hr=int(row[12:14])
        t = Time({'year': int(row[7:11]), 'month': int(mon)+1, 'day': int(row[4:6]), 'hour': hr, 'minute': int(row[15:17]), 'second':float(row[18:25])},scale='utc').unix
        times.append(t)
    time_arr = np.array(times)

    #change to dict (use same format as h5 reads)
    dataDict = {}
    obsDict = {}
    obsDict['time'] = time_arr
    tunDict = {}
    freqs = data.columns[5:].values #frequency table
    tunDict['freqs'] = freqs
    data_arr = data.iloc[:,5:].values
    tunDict['XX'] = data_arr
    nanArray = np.empty((data_arr.shape))
    nanArray[:] = np.nan
    tunDict['Saturation'] = nanArray
    obsDict['Tuning1'] = tunDict
    dataDict['Observation1'] = obsDict

    return dataDict
