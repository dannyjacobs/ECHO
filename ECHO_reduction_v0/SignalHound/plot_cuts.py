import sys
import numpy as n
#import matplotlib.pyplot as plt
from pylab import *
import healpy as hp
from matplotlib import cm
import optparse


######################### Opts #############################

o = optparse.OptionParser()
o.set_description('Generates a healpix beam given precompiled, combined spectral/position data.')
o.add_option('--times',type=str,help="file with list of start and stop gps times")
o.add_option('--nsides',type=int,default=8,help='Number of sides for Healpix plotting. Default is 8.')
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
    xi = n.arange(xmin, xmax+binsize, binsize)
    yi = n.arange(ymin, ymax+binsize, binsize)
    xi, yi = n.meshgrid(xi,yi)

    # make the grid.
    grid = n.zeros(xi.shape, dtype=x.dtype)
    nrow, ncol = grid.shape
    if retbin: bins = n.copy(grid)
    if retrms: rmsBins = n.copy(grid)

    # make arrays to store counts/rms for Healpix data
    gcounts = n.zeros_like(z)
    grms = n.zeros_like(z)

    # create list in same shape as grid to store indices
    if retloc:
        wherebin = n.copy(grid)
        wherebin = wherebin.tolist()
    # fill in the grid.
    for row in range(nrow):
        for col in range(ncol):
            xc = xi[row, col]    # x coordinate.
            yc = yi[row, col]    # y coordinate.

            # find the position that xc and yc correspond to.
            posx = n.abs(x - xc)
            posy = n.abs(y - yc)
            ibin = n.logical_and(posx < binsize/2., posy < binsize/2.)
            ind  = n.where(ibin == True)[0]

            # fill the bin.
            bin = z[ibin]
            gcounts[ibin] = n.sum(ibin) # update counts at each x position
            if retloc: wherebin[row][col] = ind
            if retbin: bins[row, col] = bin.size
            if bin.size != 0:
                binval = n.median(bin)
                grid[row, col] = binval
                if retrms:
                    rmsBins[row,col] = n.std(bin)
                    grms[ibin] = n.std(bin)
            else:
                grid[row, col] = n.nan   # fill empty bins with nans.
                if retrms:
                    rmsBins[row,col] = n.nan
                    grms[ibin] = n.nan

    # return the grid
    if retbin:
        if retloc:
            if retrms:
                return n.ma.masked_invalid(grid), bins, n.ma.masked_invalid(rmsBins), wherebin, xi, yi, gcounts, grms
            else:
                return n.ma.masked_invalid(grid), bins, wherebin, xi, yi, gcounts, grms
        else:
            return n.ma.masked_invalid(grid), bins, xi, yi, gcounts, grms
    else:
        if retloc:
            if retrms:
                return n.ma.masked_invalid(grid), n.ma.masked_invalid(rmsBins), wherebin, xi, yi, gcounts, grms
            else:
                return n.ma.masked_invalid(grid), wherebin, xi, yi, gcounts, grms
        else:
            if retrms:
                return n.ma.masked_invalid(grid), n.ma.masked_invalid(rmsBins), xi, yi, gcounts, grms
            else:
                return n.ma.masked_invalid(grid), xi, yi, gcounts, grms
# end griddata

def latlon2xy(lat,lon,lat0,lon0):
    x = r_earth*(lon - lon0)*(n.pi/180)
    y = r_earth*(lat - lat0)*(n.pi/180)
    return x,y
# end latlon2xy

def to_spherical(x,y,z):
    # x and y are cartesian coordinates
    # z is relative altitude
    rhos = n.sqrt(x**2+y**2+z**2)
    thetas = n.arccos(z/rhos) # Zentih angle
    phis = n.arctan2(y,x) # Azimuthal angle
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

# Constants
r_earth = 6371000
fIndex = 2253 # Index of 138 MHz broadcast signal
c = 3e8 #m/s
f = 138e6 #MHz
lamb = c/f

# Initialize array to store data
rawData = []

# Read in preprocessed files.
# The first three lines contain comment and formatting information.
# The fourth line on contain data.
# Column format is: index, Time (gps), latitude (deg), longitude (deg), altitude (m),
# yaw (deg), spectrum (Vrms)
date = args[0].split('_')[2]
for inFile in args:
    lines = open(inFile).readlines()
    freqs = map(float,lines[2].split(','))
    freqs = n.array(freqs)
    # Add information from each flight to rawData array
    for line in lines[3:]:
        rawData.append(map(float,line.strip('\n').split(',')))
rawData = n.array(rawData)

# Extract information from rawData array
(times,lat,lon,alt,yaw,spectrum) = (rawData[:,1],rawData[:,2],rawData[:,3],
                                                        rawData[:,4],rawData[:,5],rawData[:,6:])
if not opts.times is None:
    timeranges = n.loadtxt(opts.times)
    inds = []
    for timerange in timeranges:
        #print times.min(),timerange.astype(int) ,times.max()
        inds.append(n.logical_and(times>timerange[0],times<timerange[1]))
        #print n.sum(inds[-1])/float(len(times))
    inds = n.sum(inds,axis=0).astype(n.bool)
    rawData = rawData[inds]
    (times,lat,lon,alt,yaw,spectrum) = (rawData[:,1],rawData[:,2],rawData[:,3],
                                                            rawData[:,4],rawData[:,5],rawData[:,6:])


lat0,lon0 = (33.3111915588378906,-111.892097473144531)
outfilename = 'mwa_EWdipole'

# Convert lat/lon to x/y
x,y = latlon2xy(lat,lon,lat0,lon0)
# Obtain spherical coordinates for x, y, and alt
rs,thetas,phis = to_spherical(x,y,alt)


# 'z' will set color value for gridded data (power value)
freqIndex = n.argwhere(freqs == 137.5).squeeze()
print freqIndex
print freqs[freqIndex]
# Only extract information from appropriate column
z = spectrum[:,freqIndex] # In dB from Signal Hound
# Distance normalization
r0 = 50 # reference position for distance normalization (unit: meters)
z = z+2*n.log10(rs/r0)
z = z-z.max()



# Set binsize (used in function griddata).  Affects the apparent size of the pixels on
# the plot created below.
binsize=5
# Obtain gridded data
grid,bins,rmsBins,binloc,xg,yg,gcounts,grms = griddata(x,y,z,binsize=binsize)



# Healpix things
nsides = opts.nsides
nPixels = hp.nside2npix(nsides)
hz = n.zeros(nPixels)
hcounts = n.zeros(nPixels)
hrms = n.zeros(nPixels)
# Find pixel # for a given theta and phi
pixInd = hp.ang2pix(nsides,thetas,phis,nest=False)
# Set pixel values at pixInd to power values
hz[pixInd] = z
hcounts[pixInd] = gcounts
hrms[pixInd] = grms
# Grey out pixels with no measurements
hz[hz == 0] = n.nan
hcounts[hcounts == 0] = n.nan
hrms[hrms == 0] = n.nan
'''
# Write healpix maps to fits files
hp.write_map(str(nsides)+'_power_'+outfilename+'.fits',hz)
hp.write_map(str(nsides)+'_rms_'+outfilename+'.fits',hrms)
hp.write_map(str(nsides)+'_counts_'+outfilename+'.fits',hcounts)
'''


######################## Plotting ###########################

# Obtain bounds for plotting window
extent = (x.min(), x.max(), y.min(), y.max())
# Compute quartiles for scaling of colorbar
fq = n.percentile(z,10)
uq = n.percentile(z,80)
# Change colormap for Healpix colorbars
bonemap = cm.bone_r
bonemap.set_under('0.75')
gnuplotmap = cm.gnuplot
gnuplotmap.set_under('0.75')


# Plot Healpix map(s)
title = 'MWA EW Dipole'
rot = [90,180,0] # Rotation for plotting view with N/S (up/down) & E/W (left/right)
hp.mollview(hz,title='Beam for '+title,unit=r'dB',format='%d',rot=rot,cmap=gnuplotmap)
#plt.savefig(str(nsides)+'_beam_'+outfilename+'.png')
#hp.mollview(hcounts,title='Counts for '+title,rot=rot,cmap='bone_r',max=25)
#plt.savefig(str(nsides)+'_counts_'+outfilename+'.png')
#hp.mollview(hrms,title='RMS for '+title,unit=r'dB',rot=rot,format='%d',cmap=gnuplotmap)
#plt.savefig(str(nsides)+'_rms'+outfilename+'.png')

plt.show()

'''

subplot(211)
plot(times,lat-lat.min(),label='lat [d]')
plot(times,lon-lon.min(),label='lon [d]')
legend()
subplot(212)
plot(times,alt-alt.min(),'.',label='alt [m]')
twinx()
plot(times,yaw,label='yaw [d]')
legend()

figure()
plot(times,z)
title('Power vs Time (v2)')

show()
'''

######################################################
