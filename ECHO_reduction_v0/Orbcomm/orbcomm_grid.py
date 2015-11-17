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
import numpy as n
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import scipy.interpolate as sin
import healpy as hp
from matplotlib import cm
import optparse


######################### Opts #############################

o = optparse.OptionParser()
o.set_description('Generates a healpix beam given precompiled, combined spectral/position data.')
o.add_option('--ant',type=str,help='Default is North')
o.add_option('--dipole',type=str,help='Dipole of interest')
o.add_option('--nsides',type=int,default=8,help='Number of sides for Healpix plotting. Default is 8.')
o.add_option('--trans',type=str,help='Polarization of Bicolog antenna onboard drone.')
o.add_option('--times',type=str,
    help="file with list of start and stop gps times")
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


def find_peak(f,x,fmin=0,fmax=500):
    # f = frequencies in MHz
    # x = spectrum
    # fmin,fmax range in which to search for peak
    fchans = n.argwhere(n.logical_and(f>fmin,f<fmax))
    peak = x[fchans].max()
    maxfreq = f[fchans[x[fchans].argmax()]]
    peakrms = n.mean(x[fchans.max():fchans.max()+100])
    return maxfreq,peak,peakrms
# end find_rms

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

# Check for valid transmitter polarization
cont = False
if opts.trans == 'NS' or opts.trans == 'EW':
    cont = True
if not cont:
    print "\nPlease enter a valid transmitter polarization (NS or EW)\n"
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
    # Add information from each flight to rawData array
    for line in lines[3:]:
        rawData.append(map(float,line.strip('\n').split(',')))
rawData = n.array(rawData)

# Extract information from rawData array
(times,lat,lon,alt,yaw) = (rawData[:,1],rawData[:,2],rawData[:,3],rawData[:,4],rawData[:,5])
if not opts.times is None:
    timeranges = n.loadtxt(opts.times)
    inds = []
    for timerange in timeranges:
        print times.min(),timerange.astype(int) ,times.max()
        inds.append(n.logical_and(times>timerange[0],times<timerange[1]))
        print n.sum(inds[-1])/float(len(times))
    inds = n.sum(inds,axis=0).astype(n.bool)
    rawData = rawData[inds]
    (times,lat,lon,alt,yaw) = (rawData[:,1],rawData[:,2],rawData[:,3],rawData[:,4],rawData[:,5])

# Future save file formatting/spectral extraction and validity check
if opts.ant == 'N': # North antenna
    lat0,lon0 = (38.4248532,-79.8503723)
    if opts.dipole == 'NS': # N-NS
        outfilename = 'Nant_NSdipole_'+opts.trans+'transmitter'
        spectrum = rawData[:,12:17]
    elif opts.dipole == 'EW': # N-EW
        outfilename = 'Nant_EWdipole_'+opts.trans+'transmitter'
        spectrum = rawData[:,24:29]
    else:
        print "\nPlease enter a valid dipole orientation (NS or EW)\n"
        sys.exit()
elif opts.ant == 'S': # South antenna
    lat0,lon0 = (38.4239235,-79.8503418)
    if opts.dipole == 'NS': # S-NS
        outfilename = 'Sant_NSdipole_'+opts.trans+'transmitter'
        spectrum = rawData[:,6:11]
    elif opts.dipole == 'EW': #S-EW
        outfilename = 'Sant_EWdipole_'+opts.trans+'transmitter'
        spectrum = rawData[:,18:23]
    else:
        print "\nPlease enter a valid dipole orientation (NS or EW)\n"
        sys.exit()
else: # Invalid antenna location passed by user
    print "\nPlease enter a valid antenna (N or S)\n"
    sys.exit()

# Convert lat/lon to x/y
x,y = latlon2xy(lat,lon,lat0,lon0)
# Obtain spherical coordinates for x, y, and alt
rs,thetas,phis = to_spherical(x,y,alt)



# 'z' will set color value for gridded data (power value)
freqIndex = n.argmax(spectrum[0,:])
# Only extract information from appropriate column
z = spectrum[:,freqIndex]
# Distance normalization
r0 = 100 # reference position for distance normalization (unit: meters)
z = n.log10((2*z**2)*(rs/r0)**2)
z = 10*(z-z.max()) # log(V^2) -> dB and normalization for healpix plotting range [-inf,0]



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
# Write healpix maps to fits files
hp.write_map(str(nsides)+'_power_'+outfilename+'.fits',hz)
hp.write_map(str(nsides)+'_rms_'+outfilename+'.fits',hrms)
hp.write_map(str(nsides)+'_counts_'+outfilename+'.fits',hcounts)



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
title = opts.ant+' Antenna, '+opts.dipole+' Dipole, '+opts.trans+' Transmitter Polarization'
rot = [90,90,0] # Rotation for plotting view with N/S (up/down) & E/W (left/right)
hp.mollview(hz,title='Beam for '+title,unit=r'dB',format='%d',rot=rot,cmap=gnuplotmap)
plt.savefig(str(nsides)+'_beam_'+outfilename+'.png')
hp.mollview(hcounts,title='Counts for '+title,rot=rot,cmap='bone_r',max=25)
plt.savefig(str(nsides)+'_counts_'+outfilename+'.png')
hp.mollview(hrms,title='RMS for '+title,unit=r'dB',rot=rot,format='%d',cmap=gnuplotmap)
plt.savefig(str(nsides)+'_rms'+outfilename+'.png')


plt.show()


######################################################

'''
################### Outlier Elimination #######################
# Remove outliers
outInd = n.where(z<-70)[0]
x[outInd],y[outInd],z[outInd],alt[outInd],times[outInd] = (n.nan,n.nan,n.nan,n.nan,n.nan)
x,y,z,alt,times = (x[n.isnan(x) == False],y[n.isnan(y) == False],z[n.isnan(z) == False],
                    alt[n.isnan(alt) == False],times[n.isnan(times) == False])
rs[outInd],thetas[outInd],phis[outInd] = (n.nan,n.nan,n.nan)
rs,thetas,phis = (rs[n.isnan(rs) == False],thetas[n.isnan(thetas) == False],
                    phis[n.isnan(phis) == False])

zind = n.where(z>-8.8)[0]
times,z,thetas,phis,x,y,alt,validPts=(times[zind],z[zind],thetas[zind],phis[zind],
                                          x[zind],y[zind],alt[zind],validPts[zind])
times,z,thetas,phis,x,y,alt=(times[validPts],z[validPts],thetas[validPts],
                                          phis[validPts],x[validPts],y[validPts],alt[validPts])





#################### Extraneous Plots #######################
plt.plot(thetas,z,'.')
plt.plot(thetas,n.sin(2*n.pi*n.cos(thetas)*0.5/lamb)**2*4e-9,'r--')
plt.plot(thetas,(n.cos(thetas)**2)*n.sin(2*n.pi*n.cos(thetas)*0.5/lamb)**2*4e-9,'b--')
plt.xlabel(r'$\theta$')
plt.ylim([0,1e-8])

plt.plot(times,z)
plt.ylabel(r'V$^2$')
plt.xlabel('time (s)')
plt.show()

plt.plot(times,z,'b-')
plt.xlabel(r't (s)')
plt.ylabel(r'V $^2$')
plt.twinx()
plt.plot(times,yaw,'k-',alpha=0.5)
plt.ylabel('Yaw (deg)')

# Plot power and rms per bin
plt.figure(figsize=(15,6))
plt.subplot(121)
plt.plot(0,0,'+',ms=25)
plt.imshow(grid,extent=extent,cmap='gnuplot',origin='lower',vmin=-7,vmax=z.max(),
                    interpolation='nearest',aspect='auto')
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.title(r'Power (V$^2$)')
plt.colorbar()

plt.subplot(122)
plt.plot(0,0,'+',ms=25)
plt.imshow(rmsBins,extent=extent,cmap='gnuplot',origin='lower',vmin=rmsBins.min(),vmax=1.5,
                    aspect='auto',interpolation='nearest')
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.title(r'RMS (V$^2$)') # Need to figure out how to place this by the colorbar
plt.colorbar() # Optional layout change: orientation='horizontal'
plt.subplots_adjust(left=0.05,right=1,wspace=0.15) # Layout formatting
plt.savefig('power_rms_'+date+'.png')


# Plot zenith pass(es)
plt.figure(figsize=(14,5))
# EW cut (x)
plt.subplot(121)
gridx,gridy=grid.shape
xind=int(gridx/2.)
yind=int(gridy/2.)
plt.errorbar(xg[0,:],grid[xind,:],yerr=rmsBins[xind,:],fmt='k.')
plt.errorbar(xg[0,:],grid[xind+1,:],yerr=rmsBins[xind+1,:],fmt='c.')
plt.xlim([xg[0,:].min(),xg[0,:].max()])
#plt.ylim([0,1e-8])
plt.xlabel('x (m)')
plt.ylabel(r'Power (V$^2$)')
plt.title('EW Cut')
#NS cut (y)
plt.subplot(122)
plt.errorbar(yg[:,0],grid[:,yind],yerr=rmsBins[:,yind],fmt='k.')
plt.errorbar(yg[:,0],grid[:,yind+1],yerr=rmsBins[:,yind+1],fmt='c.')
plt.xlim([yg[:,0].min()-1,yg[:,0].max()+1])
plt.xlabel('y (m)')
plt.ylabel('Power (dBm)')
plt.title('NS Cut')
plt.subplots_adjust(left=0.05,right=0.97,wspace=0.15) # Layout formatting
plt.savefig('cuts_'+date+'.png')


# Plt counts per bin
plt.figure()
plt.imshow(bins, extent=extent, cmap=bonemap, origin='lower', vmin=0, vmax=4,
                    aspect='auto', interpolation='nearest')
plt.plot(0,0,'+',ms=25)
plt.xlim([extent[0],extent[1]])
plt.ylim([extent[2],extent[3]])
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.title('Counts per Bin') # Need to figure out how to place this by the colorbar
plt.colorbar()
plt.savefig('counts_'+date+'.png')





##################### Theor Beam #########################
# Compare theoretical ratio of beam
hratio = n.zeros(nPixels)
hfunc = n.sin(2*phis)**2*n.sin(2*n.pi*0.5*n.cos(thetas)/lamb)**2
hfunc = n.log10(hfunc)
#hfunc = z/hfunc
hratio[pixInd] = hfunc
hp.mollview(hratio,rot=[90,90,0],min=-4,max=0.0,format='%d')
hp.mollview(hz+0.5,rot=[90,90,0],max=0.0,min=-4,format='%d')
plt.show()






##################### Waypoint Info ########################
# Waypoint times read in
wayptFile = sys.argv[1]
waypts = []
ranges = []
wayptLines = open(wayptFile).readlines()
for line in wayptLines[1:]:
    waypts.append(map(float,line.split(' ')[:]))
waypts = n.array(waypts)
# Filter data around waypoints
validPts =n.array([inrange(waypts[:,2],t) for t in times])

print "Waypoints range: %.2f, %.2f, %.2f" %(waypts[0,2],waypts[-1,2],waypts[-1,2]-waypts[0,2])
print "Times range: %.2f, %.2f, %.2f" %(times[0],times[-1],times[-1]-times[0])
'''
