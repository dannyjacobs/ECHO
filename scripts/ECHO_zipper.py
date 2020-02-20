import numpy as np
import time,optparse,sys
from glob import glob

from astropy.time import Time
from ECHO.read_utils import get_data
from ECHO.time_utils import unix_to_gps
from ECHO.read_utils import read_apm_logs,flag_angles,apply_flagtimes,\
    read_orbcomm_spectrum,channel_select,interp_rx,dB,read_echo_spectrum
o = optparse.OptionParser()
o.set_description("""Combine apm and reciever data.
        Interpolates on the rx power and converts to local XYZ""")
o.add_option('--rx_files',type=str,
    help='Receiver spectrum files glob (ie as a string with quotes)')
o.add_option('--apm_files',type=str,
    help='APM log file glob (ie as a string with quotes)')
o.add_option('--acc_file',type=str,
    help='Accumulated output file.')
o.add_option('--lat0',type=str,
    help='Latitude of antenna under test')
o.add_option('--lon0',type=str,
    help='Longitude of antenna under test')
o.add_option('--freq',type=float,default=137.500,
    help='Transmitter freq.')
o.add_option('--pol',type=str,help='polarization for tx and rx [ex NS_NS].')
o.add_option('--rxant',type=str,help='select antenna from rx data. N or S for orbcomm data')
opts,args = o.parse_args(sys.argv[1:])

#find the data files
rxfiles = glob(opts.rx_files)
assert(len(rxfiles)>0)
print("found",len(rxfiles),"rx data files")

apm_files = glob(opts.apm_files)
assert(len(apm_files)>0)
print("found",len(apm_files),"apm files")
#load the apm data
positiontimes,positions,angletimes,angles,cmdtimes,CMDnums = read_apm_logs(apm_files)



#load the receiver data
rx_files = glob(opts.rx_files)
assert(len(rx_files)>0)
if rx_files[0].find('satpower')!=-1:#we're in orbcomm town
    pol = opts.pol.split('_')[1]
    rxtimes,freqs,rxspectrum = read_orbcomm_spectrum(rx_files,opts.rxant,pol)
else: #read the default echo rx spectrum
    rxtimes,freqs,rxspectrum = read_echo_spectrum(rx_files)

#get the power in our current channel
rx_power = channel_select(freqs,rxspectrum,opts.freq)
freqs = np.array([opts.freq])

#interpolate the rx data down to match the gps times
rx_interp = interp_rx(positiontimes,rxtimes,rx_power)


#flag based on yaws
print("flagging based on yaw")
yawmask,badyawtimes = flag_angles(angletimes,angles,2)
posmask = apply_flagtimes(positiontimes,badyawtimes,1.0)
rx_interp = np.ma.masked_where(posmask,rx_interp)
print("total flags after yaw flagging:",np.sum(rx_interp.mask))


#flag based on waypoints
print("flagging based on waypoints")
cmdmask = apply_flagtimes(positiontimes,cmdtimes,0.5)
rx_interp = np.ma.masked_where(cmdmask,rx_interp)
print("total flags after cmd flagging:",np.sum(rx_interp.mask))

#output the zippered data in standard ECHO accumulated format
"""
# Accumulated data for 2016-07-21,23:34:19.980
# Column Format:Time [GPS s],Lat [deg],Lon [deg],Rel Alt [m],Radio Spectrum
# lat0,lon0: 34.6205940,-112.4479370
# Freqs:
"""
F = open(opts.acc_file,'w')
F.write("# Accumulated data for "+positiontimes[0].iso+'\n')
F.write("# Column Format:Time [GPS s],Lat [deg],Lon [deg],Rel Alt [m],Yaw [deg],Radio Spectrum"+'\n')
F.write("# lat0, lon0 (deg): {lat0}, {lon0}".format(lat0=opts.lat0,lon0=opts.lon0)+'\n')
F.write("# Freqs (MHz): "+','.join(freqs.astype(str))+'\n')
for i in range(len(positiontimes)):
    if rx_interp.mask[i]:continue
    F.write(str(positiontimes[i].gps))
    F.write(',')
    F.write(','.join(positions[:,i].astype(str)))
    F.write(',')
    F.write(','.join(angles[:,i].astype(str)))
    F.write(',')
    try:
        F.write(map(str,rx_interp[i]))
    except(TypeError):
        F.write(str(rx_interp[i]))
    F.write('\n')
F.close()
