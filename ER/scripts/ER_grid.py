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

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import scipy.interpolate as sin
import healpy as hp
from matplotlib import cm
import optparse


######################### Opts #############################

o = optparse.OptionParser()
o.set_description('Generates a healpix beam given precompiled, combined spectral/position data.')
o.add_option('--nsides',type=int,default=8,
    help='Number of sides for Healpix plotting. Default is 8.')
o.add_option('--trans',type=str,help='Polarization of Bicolog antenna onboard drone.')
o.add_option('--times',type=str,
    help="file with list of start and stop gps times")
o.add_option('--lat0',type=float,help='latitude of antenna under test')
o.add_option('--lon0',type=float,help='longitude of antenna under test')
o.add_option('--freq',type=float,default=137.500,
        help='Frequency to look for in data')
opts,args = o.parse_args(sys.argv[1:])

######################## Functions #########################

#griddata.py - 2010-07-11 ccampo
#Obtained via http://wiki.scipy.org/Cookbook/Matplotlib/Gridding_irregularly_spaced_data
# Modified
def griddata(x, y, z, binsize=0.01, retbin=True, retloc=True, retrms=True):
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
rawData = np.array(rawData)

# Extract information from rawData array
(times,lat,lon,alt,spectrum) = (rawData[:,1],rawData[:,2],rawData[:,3],rawData[:,4],rawData[:,5:])
if not opts.times is None:
    timeranges = np.loadtxt(opts.times)
    inds = []
    for timerange in timeranges:
        print times.min(),timerange.astype(int) ,times.max()
        inds.append(np.logical_and(times>timerange[0],times<timerange[1]))
        print np.sum(inds[-1])/float(len(times))
    inds = np.sum(inds,axis=0).astype(np.bool)
    rawData = rawData[inds]
    (times,lat,lon,alt,spectrum) = (rawData[:,1],rawData[:,2],rawData[:,3],rawData[:,4],rawData[:,5:])


# Convert lat/lon to x/y
x,y = latlon2xy(lat,lon,opts.lat0,opts.lon0)
# Obtain spherical coordinates for x, y, and alt
rs,thetas,phis = to_spherical(x,y,alt)



# 'z' will set color value for gridded data (power value)
# Only extract information from appropriate column
z = spectrum[:,freqIndex]
# Distance normalization
r0 = 100 # reference position for distance normalization (unit: meters)
z = np.log10((2*z**2)*(rs/r0)**2)
z = 10*(z-z.max()) # log(V^2) -> dB and normalization for healpix plotting range [-inf,0]



# Set binsize (used in function griddata).  Affects the apparent size of the pixels on
# the plot created below.
binsize=5
# Obtain gridded data
grid,bins,rmsBins,binloc,xg,yg,gcounts,grms = griddata(x,y,z,binsize=binsize)



# Healpix things
nsides = opts.nsides
nPixels = hp.nside2npix(nsides)
hz = np.zeros(nPixels)
hcounts = np.zeros(nPixels)
hrms = np.zeros(nPixels)
# Find pixel # for a given theta and phi
pixInd = hp.ang2pix(nsides,thetas,phis,nest=False)
# Set pixel values at pixInd to power values
hz[pixInd] = z
hcounts[pixInd] = gcounts
hrms[pixInd] = grms
# Grey out pixels with no measurements
hz[hz == 0] = np.nan
hcounts[hcounts == 0] = np.nan
hrms[hrms == 0] = np.nan
# Write healpix maps to fits files
#hp.write_map(str(nsides)+'_power_'+outfilename+'.fits',hz)
#hp.write_map(str(nsides)+'_rms_'+outfilename+'.fits',hrms)
#hp.write_map(str(nsides)+'_counts_'+outfilename+'.fits',hcounts)



######################## Plotting ###########################

# Obtain bounds for plotting window
extent = (x.min(), x.max(), y.min(), y.max())
# Compute quartiles for scaling of colorbar
fq = np.percentile(z,10)
uq = np.percentile(z,80)
# Change colormap for Healpix colorbars
bonemap = cm.bone_r
bonemap.set_under('0.75')
gnuplotmap = cm.gnuplot
gnuplotmap.set_under('0.75')


# Plot Healpix map(s)
''' NEED TO CHANGE title BELOW '''
title = opts.trans+' Transmitter Polarization'
rot = [90,90,0] # Rotation for plotting view with N/S (up/down) & E/W (left/right)
hp.mollview(hz,title='Beam for '+title,unit=r'dB',format='%d',rot=rot,cmap=gnuplotmap)
#plt.savefig(str(nsides)+'_beam_'+outfilename+'.png')
hp.mollview(hcounts,title='Counts for '+title,rot=rot,cmap='bone_r',max=25)
#plt.savefig(str(nsides)+'_counts_'+outfilename+'.png')
hp.mollview(hrms,title='RMS for '+title,unit=r'dB',rot=rot,format='%d',cmap=gnuplotmap)
#plt.savefig(str(nsides)+'_rms'+outfilename+'.png')


plt.show()


######################################################
