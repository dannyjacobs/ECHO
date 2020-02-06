import numpy as np
import time,optparse,sys
from glob import glob
import healpy as hp

from astropy.time import Time
from ECHO.read_utils import get_data
from ECHO.plot_utils import make_beam,grid_to_healpix
from ECHO.time_utils import unix_to_gps
from ECHO.read_utils import read_apm_logs,flag_angles,apply_flagtimes,read_orbcomm_spectrum,channel_select,interp_rx,dB
o = optparse.OptionParser()
o.add_option('--nsides',type=int,default=8,
    help='Number of sides for Healpix plotting (Default = 8)')
opts,args = o.parse_args(sys.argv[1:])

infile = sys.argv[1]
spec_times,spec_raw,freqs,lats,lons,alts = get_data(infile,
                                                filetype='echo')

hpx_beam,hpx_rms,hpx_counts = grid_to_healpix(lats[1:],lons[1:],
                                                alts,spec_raw,
                                                lat0=lats[0],
                                                lon0=lons[0],
                                                nside=opts.nsides)

hp.write_map(infile[:-4]+'_'+str(opts.nsides)+'_beam.fits',hpx_beam)
hp.write_map(infile[:-4]+'_'+str(opts.nsides)+'_rms.fits',hpx_rms)
hp.write_map(infile[:-4]+'_'+str(opts.nsides)+'_counts.fits',hpx_counts)
