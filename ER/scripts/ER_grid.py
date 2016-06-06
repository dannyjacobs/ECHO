'''

Author: Jacob Burba
Created: 08/14/15

This script currently accepts previously compiled APM/spectral files, and grids the data using a
function obtained online from the Scipy Cookbook.  The data is then used to produce Healpix
maps of power per pixel, counts per pixel, and rms per pixel.  The antenna location, dipole
of interest, and transmitter polarization must be passed by the user.  An example call
for the N antenna, NS dipole, with a NS transmitter polarization and nsides = 8 can be
seen as follows:

python orbgrid.py Aug13_combined_NStransmitter.txt --ant N --dipole NS --trans NS --nsides 8

    --ant: Antenna of interest (N or S).  Must be passed by user.
    --dipole: Dipole of interest (NS or EW).  Must be passed by user.
    --trans: Polarization of Bicolog antenna (NS or EW).  Must be passed by user.
    --nsides: Determines the number of pixels in the generated Healpix maps.
                - Value must be a power of 2.  See Healpix documentation for further information.
                   This parameter does not need to be passed by the user.  Default is 8.

The files and parameters can be passed in any order.  The program will read them in and
process them accordingly.

Six output files will be created upon this script exiting.  There will be three plots, displayed and
saved as .png's, which contain Healpix maps of the the beam, counts, and rms for the given
dipole.  The other three will be .fits files which contain the values being plotted in the created
Healpix maps (i.e. power, counts, and rms).

'''

import sys,optparse,warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import scipy.interpolate as sin
import healpy as hp

from matplotlib import cm
from matplotlib.collections import PolyCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.gridspec as gridspec
from healpy import _healpy_pixel_lib as pixlib


######################### Opts #############################

o = optparse.OptionParser()
o.set_description('Generates a healpix beam given precompiled, combined spectral/position data.')
o.add_option('--nsides',type=int,default=8,
    help='Number of sides for Healpix plotting. Default is 8.')
o.add_option('--trans',type=str,
    help='Polarization of Bicolog antenna onboard drone.')
o.add_option('--times',type=str,
    help="file with list of start and stop gps times")
o.add_option('--waypts',type=str,
    help='file with list of waypoint execution times')
o.add_option('--lat0',type=float,
    help='latitude of antenna under test')
o.add_option('--lon0',type=float,
    help='longitude of antenna under test')
o.add_option('--freq',type=float,default=137.500,
    help='Frequency to look for in data')
opts,args = o.parse_args(sys.argv[1:])

######################## Functions #########################

def make_beam(lats,lons,alts,spec_raw,freq_chan,lat0=0.0,lon0=0.0,nsides=8,volts=False,normalize=False):
    # Convert lat/lon to x/y
    x,y = latlon2xy(lats,lons,lat0,lon0)
    # Obtain spherical coordinates for x, y, and alt
    rs,thetas,phis = to_spherical(x,y,alts)


    # Only extract information from appropriate column (index = 10)
    z = spec_raw[:,freq_chan].copy()
    if volts:
        # Distance normalization
        r0 = 100 # reference position for distance normalization (unit: meters)
        z = 10*np.log10((2*z**2)*(rs/r0)**2)
    if normalize:
        z -= z.max() # Scaled on [-infty,0]

    # Set binsize (used in function grid_data)
    # Affects the apparent size of the pixels on the plot created below.
    binsize=5
    # Obtain gridded data
    grid,bins,rmsBins,binloc,xg,yg,gcounts,grms = grid_data(x,y,z,binsize=binsize)

    # Healpix things
    nPixels = hp.nside2npix(nsides)
    hpx_beam = np.zeros(nPixels)
    hpx_counts = np.zeros(nPixels)
    hpx_rms = np.zeros(nPixels)
    # Find pixel # for a given theta and phi
    pixInd = hp.ang2pix(nsides,thetas,phis,nest=False)
    # Set pixel values at pixInd to power values
    hpx_beam[pixInd] = z
    hpx_counts[pixInd] = gcounts
    hpx_rms[pixInd] = grms
    # Grey out pixels with no measurements
    hpx_beam[hpx_beam == 0] = hp.UNSEEN
    hpx_counts[hpx_counts == 0] = hp.UNSEEN
    hpx_rms[hpx_rms == 0] = hp.UNSEEN

    return hp.ma(hpx_beam),hp.ma(hpx_counts),hp.ma(hpx_rms)

#griddata.py - 2010-07-11 ccampo
#Obtained via http://wiki.scipy.org/Cookbook/Matplotlib/Gridding_irregularly_spaced_data
# Modified
def grid_data(x, y, z, binsize=0.01, retbin=True, retloc=True, retrms=True):
    # get extrema values.
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()
    # make coordinate arrays.
    xi = np.arange(xmin, xmax+binsize, binsize)
    yi = np.arange(ymin, ymax+binsize, binsize)
    xi, yi = np.meshgrid(xi,yi)

    # make the grid.
    grid = np.zeros(xi.shape, dtype=x.dtype)
    nrow, ncol = grid.shape
    if retbin: bins = np.copy(grid)
    if retrms: rmsBins = np.copy(grid)

    # make arrays to store counts/rms for Healpix data
    gcounts = np.zeros_like(z)
    grms = np.zeros_like(z)

    # create list in same shape as grid to store indices
    if retloc:
        wherebin = np.copy(grid)
        wherebin = wherebin.tolist()
    # fill in the grid.
    for row in range(nrow):
        for col in range(ncol):
            xc = xi[row, col]    # x coordinate.
            yc = yi[row, col]    # y coordinate.

            # find the position that xc and yc correspond to.
            posx = np.abs(x - xc)
            posy = np.abs(y - yc)
            ibin = np.logical_and(posx < binsize/2., posy < binsize/2.)
            ind  = np.where(ibin == True)[0]

            # fill the bin.
            bin = z[ibin]
            gcounts[ibin] = np.sum(ibin) # update counts at each x position
            if retloc: wherebin[row][col] = ind
            if retbin: bins[row, col] = bin.size
            if bin.size != 0:
                binval = np.median(bin)
                grid[row, col] = binval
                if retrms:
                    rmsBins[row,col] = np.std(bin)
                    grms[ibin] = np.std(bin)
            else:
                grid[row, col] = np.nan   # fill empty bins with nans.
                if retrms:
                    rmsBins[row,col] = np.nan
                    grms[ibin] = np.nan

    # return the grid
    if retbin:
        if retloc:
            if retrms:
                return np.ma.masked_invalid(grid), bins, np.ma.masked_invalid(rmsBins), wherebin, xi, yi, gcounts, grms
            else:
                return np.ma.masked_invalid(grid), bins, wherebin, xi, yi, gcounts, grms
        else:
            return np.ma.masked_invalid(grid), bins, xi, yi, gcounts, grms
    else:
        if retloc:
            if retrms:
                return np.ma.masked_invalid(grid), np.ma.masked_invalid(rmsBins), wherebin, xi, yi, gcounts, grms
            else:
                return np.ma.masked_invalid(grid), wherebin, xi, yi, gcounts, grms
        else:
            if retrms:
                return np.ma.masked_invalid(grid), np.ma.masked_invalid(rmsBins), xi, yi, gcounts, grms
            else:
                return np.ma.masked_invalid(grid), xi, yi, gcounts, grms
# end griddata


def make_polycoll(hpx_beam,plot_lim=[-90,-50],nsides=8):
    pix = np.where(np.isnan(hpx_beam)==False)[0]
    boundaries = hp.boundaries(nsides,pix)
    verts = np.swapaxes(boundaries[:,0:2,:],1,2)
    coll = PolyCollection(verts, array=hpx_beam[np.isnan(hpx_beam)==False],\
                                    cmap=cm.gnuplot,edgecolors='none')
    return coll


def find_peak(f,x,fmin=0,fmax=500):
    # f = frequencies in MHz
    # x = spectrum
    # fmin,fmax range in which to search for peak
    fchans = np.argwhere(np.logical_and(f>fmin,f<fmax))
    peak = x[fchans].max()
    maxfreq = f[fchans[x[fchans].argmax()]]
    peakrms = np.mean(x[fchans.max():fchans.max()+100])
    return maxfreq,peak,peakrms
# end find_rms

def latlon2xy(lat,lon,lat0,lon0):
    x = r_earth*(lon - lon0)*(np.pi/180)
    y = r_earth*(lat - lat0)*(np.pi/180)
    return x,y
# end latlon2xy

def to_spherical(x,y,z):
    # x and y are cartesian coordinates
    # z is relative altitude
    rhos = np.sqrt(x**2+y**2+z**2)
    thetas = np.arccos(z/rhos) # Zentih angle
    phis = np.arctan2(y,x) # Azimuthal angle
    return rhos,thetas,phis
# end to_spherical

def inrange(tr,t):
    diff = 3
    for i in range(0,len(tr)):
        if (t>=tr[i]-diff) and (t<=tr[i]+diff):
            return True
    return False
# end inrange


def get_interp_val(m,theta,phi,nest=False):
    """Return the bi-linear interpolation value of a map using 4 nearest neighbours.

    Parameters
    ----------
    m : array-like
      an healpix map, accepts masked arrays
    theta, phi : float, scalar or array-like
      angular coordinates of point at which to interpolate the map
    nest : bool
      if True, the is assumed to be in NESTED ordering.

    Returns
    -------
      val : float, scalar or arry-like
        the interpolated value(s), usual numpy broadcasting rules apply.

    """
    m2=m.ravel()
    nside=hp.pixelfunc.npix2nside(m2.size)
    if nest:
        r=pixlib._get_interpol_nest(nside,theta,phi)
    else:
        r=pixlib._get_interpol_ring(nside,theta,phi)
    p = np.array(r[0:4])
    w = np.array(r[4:8])
    w = np.ma.array(w)
    w.mask = m2[p].mask
    del r
    return np.ma.sum(m2[p]*w/np.ma.sum(w,0),0)

######################### Main #############################

# Check if user passed a combined file
if len(args) == 0:
    print "\nPlease pass a valid combined file\n"
    sys.exit()

if not opts.trans:
    print '\nPlease pass a valid transmitter polarization'
    sys.exit()

if not opts.lat0:
    print '\nPlease pass valid --lat0 and --lon0 for antenna'
    sys.exit()

# Constants
r_earth = 6371000
c = 3e8 #m/s
f = 138e6 #MHz
lamb = c/f

# Initialize array to store data
rawData = []

# Read in preprocessed files.
# The first three lines contain comment and formatting information.
# The fourth line on contain data.
# Column format is: index,Time(gps),latitude(deg),longitude(deg),altitude(m),spectrum(Vrms)
date = args[0].split('_')[2]
for inFile in args:
    lines = open(inFile).readlines()
    freqs = np.array(map(float,lines[2].rstrip('\n').split(',')))
    freqIndex = np.where(np.abs(freqs-opts.freq).min()==np.abs(freqs-opts.freq))[0]

    # Add information from each flight to rawData array
    for line in lines[3:]:
        rawData.append(map(float,line.strip('\n').split(',')))
rawData = np.array(rawData); times = rawData[:,1]
print 'Read in %d lines from %s...\n' %(rawData.shape[0],','.join(args))

if not opts.times is None:
    timeranges = np.loadtxt(opts.times)
    inds = []
    for timerange in timeranges:
        print times.min(),timerange.astype(int) ,times.max()
        #print timerange[0]-times.min(),times.max()-timerange[1]
        inds.append(np.logical_and(times>timerange[0],times<timerange[1]))
        #print inds[-1]
        print np.sum(inds[-1])/float(len(times))
    inds = np.sum(inds,axis=0).astype(np.bool)
    print 'Data shape before time filter: %d' %rawData.shape[0]
    rawData = rawData[inds];times = rawData[:,1]
    print 'Data shape after time filter: %d\n' %rawData.shape[0]

if not opts.waypts is None:
    # Waypoint times read in
    wayptFile = opts.waypts
    waypts = np.loadtxt(opts.waypts,skiprows=1,dtype=float)
    # Filter data around waypoints
    validPts =np.array([inrange(waypts,t) for t in times])
    print 'Data shape before waypoints filter: %d' %rawData.shape[0]
    rawData = rawData[validPts];times = rawData[:,1]
    print 'Data shape after waypoints filter: %d\n' %rawData.shape[0]
    #print "Waypoints range: %.2f, %.2f, %.2f" %(waypts[0,2],waypts[-1,2],waypts[-1,2]-waypts[0,2])
    #print "Times range: %.2f, %.2f, %.2f\n" %(times[0],times[-1],times[-1]-times[0])


# Extract information from rawData array
(times,lats,lons,alts,spec_raw) = (rawData[:,1],rawData[:,2],rawData[:,3],rawData[:,4],rawData[:,5:])

# Convert lat/lon to x/y
xs,ys = latlon2xy(lats,lons,opts.lat0,opts.lon0)
# Obtain spherical coordinates for x, y, and alt
rs,thetas,phis = to_spherical(xs,ys,alts)



# Set binsize (used in function griddata).  Affects the apparent size of the pixels on
# the plot created below.
binsize=5
# Obtain gridded data
grid,bins,rmsBins,binloc,xg,yg,gcounts,grms = grid_data(xs,ys,spec_raw,binsize=binsize)
# Obtain beam
hpx_beam,hpx_counts,hpx_rms = make_beam(lats,lons,alts,spec_raw,freqIndex,\
                                        lat0=opts.lat0,lon0=opts.lon0,nsides=opts.nsides)

#hp.write_map(str(opts.nsides)+'_power_ER.fits',hpx_beam)

fig = plt.figure()
gsr = gridspec.GridSpec(2, 1,height_ratios=[1,1])

beam_plot = fig.add_subplot(gsr[0],aspect='equal')
coll = make_polycoll(hpx_beam,nsides=opts.nsides)#,plot_lim=[-90,-50])
beam_plot.add_collection(coll)
beam_plot.autoscale_view()

# Position colorbar next to plot with same height as plot
divider = make_axes_locatable(beam_plot)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = fig.colorbar(coll, cax=cax, use_gridspec=True, label='dB')
#cbar.set_clim([-90,-50])

for radius_deg in [20,40,60,80]:
    r = np.sin(radius_deg*np.pi/180.)
    x = np.linspace(-r,r,100)
    beam_plot.plot(x,np.sqrt(r**2-x**2),'w-',linewidth=3)
    beam_plot.plot(x,-np.sqrt(r**2-x**2),'w-',linewidth=3)


# Cuts plot initialization
cuts_plot = fig.add_subplot(gsr[1])

#receiver coordinates
r0 = 90 # radius of sphere flown
lowest_ell = np.arccos(alts.min()/r0)
ell = np.linspace(-lowest_ell,lowest_ell)
az = np.zeros_like(ell)
xticks = [-90,-60,-40,-20,0,20,40,60,90]
beam_slice_E = get_interp_val(hpx_beam,ell,az)
beam_slice_E_err = get_interp_val(hpx_rms,ell,az)
beam_slice_H = get_interp_val(hpx_beam,ell,az+np.pi/2)
beam_slice_H_err = get_interp_val(hpx_rms,ell,az+np.pi/2)

cuts_E_line = cuts_plot.errorbar(ell*180/np.pi,beam_slice_E,\
                                                beam_slice_E_err,fmt='b.',label='ECHO [E]')
cuts_H_line = cuts_plot.errorbar(ell*180/np.pi,beam_slice_H,\
                                                beam_slice_H_err,fmt='r.',label='ECHO [H]')
cuts_plot.legend(loc='lower center')
cuts_plot.set_ylabel('dB')
cuts_plot.set_xlabel('Elevation Angle [deg]')
cuts_plot.set_xticks(xticks)


with warnings.catch_warnings():
    # This raises warnings since tight layout cannot
    # handle gridspec automatically. We are going to
    # do that manually so we can filter the warning.
    warnings.simplefilter("ignore", UserWarning)
    gsr.tight_layout(fig, rect=[0, None, None, 0.97])


plt.show()

# Write healpix maps to fits files
hp.write_map(str(opts.nsides)+'_power_'+'_'.join(args[0].split('_')[0:3])+'.fits',hpx_beam)
hp.write_map(str(opts.nsides)+'_rms_'+'_'.join(args[0].split('_')[0:3])+'.fits',hpx_rms)
hp.write_map(str(opts.nsides)+'_counts_'+'_'.join(args[0].split('_')[0:3])+'.fits',hpx_counts)


'''
######################## Plotting ###########################

# Obtain bounds for plotting window
extent = (xs.min(), xs.max(), ys.min(), ys.max())
# Compute quartiles for scaling of colorbar
fq = np.percentile(z,10)
uq = np.percentile(z,80)
# Change colormap for Healpix colorbars
bonemap = cm.bone_r
bonemap.set_under('0.75')
gnuplotmap = cm.gnuplot
gnuplotmap.set_under('0.75')


# Plot Healpix map(s)
# NEED TO CHANGE title BELOW
title = opts.trans+' Transmitter Polarization'
rot = [90,90,0] # Rotation for plotting view with N/S (up/down) & E/W (left/right)
hp.mollview(hpx_beam,title='Beam for '+title,unit=r'dB',format='%d',rot=rot,cmap=gnuplotmap)
#plt.savefig(str(nsides)+'_beam_'+outfilename+'.png')
#hp.mollview(hcounts,title='Counts for '+title,rot=rot,cmap='bone_r',max=25)
#plt.savefig(str(nsides)+'_counts_'+outfilename+'.png')
#hp.mollview(hrms,title='RMS for '+title,unit=r'dB',rot=rot,format='%d',cmap=gnuplotmap)
#plt.savefig(str(nsides)+'_rms'+outfilename+'.png')


plt.show()


######################################################
'''
