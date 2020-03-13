import numpy as np
from astropy.time import Time
from datetime import datetime



def unix_to_gps(t):
    return Time(t,scale='utc',format='unix').gps


def gps_to_HMS(t,fmt):
    t = Time(t,scale='utc',format=fmt)
    return t.iso.split(' ')[1]


def find_peak(f,x,fmin=0,fmax=500):
    # f = frequencies in MHz
    # x = spectrum
    # fmin,fmax range in which to search for peak
    fchans = np.argwhere(np.logical_and(f>fmin,f<fmax))
    peak = x[fchans].max()
    maxfreq = f[fchans[x[fchans].argmax()]]
    peakrms = np.mean(x[fchans.max():fchans.max()+100])
    return maxfreq,peak,peakrms


def inrange(tr,t,diff=3):
    for i in range(0,len(tr)):
        if (t>=tr[i]-diff) and (t<=tr[i]+diff):
            return True
    return False


def flight_time_filter(timeranges,times):
    inds = []
    for timerange in timeranges:
        inds.append(np.logical_and(times>timerange[0],
                                   times<timerange[1]))
    inds = np.sum(inds,axis=0).astype(np.bool)
    return inds


def waypt_time_filter(waypt_times,times):
    inds = np.array([inrange(waypt_times,t) for t in times])
    return inds

def DatetimetoUnix(data):
    """Function to convert timestamps to unix time through an array.

    Args:
        logged_data (array): array of data including timestamps in the first column.

    Returns:
        timeconv_data: an array of the same shape as the input array, with timestamps in unix format.

    """
    timeconv_data = data
    for row in timeconv_data:
        timestamp = row[0]
        timestamp = datetime.strptime(timestamp, '%m/%d/%Y %I:%M:%S %p')           
        timestamp = Time(timestamp, format='datetime')
        unix_time = timestamp.unix
        unix_time = unix_time + (7*3600) #MST to GMT
        row[0] = unix_time
        
    return timeconv_data