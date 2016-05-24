import numpy as np
from astropy.time import Time

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
