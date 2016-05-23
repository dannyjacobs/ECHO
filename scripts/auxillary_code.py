import numpy as np

def get_gps():
    gps_raw = []
    lines = open(opts.gps_file).readlines()
    count = len(lines)
    gps_raw = [map(float,line.rstrip('\n').split(',')) for line in lines[2:] if len(line.split(','))==4]
    return np.array(gps_raw)
# end get_gps



# Function that filters data around waypoints to avoid drone "shimmy"
def inrange(tr,t):
    diff = 3
    for i in range(0,len(tr)):
        if (t>=tr[i]-diff) and (t<=tr[i]+diff):
            return True
    return False
# End inrange



# Alternative peak_chan definition looking for maximum power frequency bin
peak_chan = np.argmax(map(float,lines[2].rstrip('\n').split(',')[1:]))+1



# Animation function declarations
ani = animation.FuncAnimation(fig,animate_spectrum,init_func=init_spectrum, interval=300, blit=True)
ani2 = animation.FuncAnimation(fig,animate_peak,init_func=init_peak, interval=300)



# Additional Healpix plotting commands used in ECHO_*_v0.0
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
# Write healpix maps to fits files
hp.write_map(str(nsides)+'_power_'+outfilename+'.fits',hz)
hp.write_map(str(nsides)+'_rms_'+outfilename+'.fits',hrms)
hp.write_map(str(nsides)+'_counts_'+outfilename+'.fits',hcounts)



# Old bits for combnined plotting and accumulating script
# Auxillary option parser arguments
o.add_option('--acc',action='store_true',help='Specify if GPS and spectral data are already combined')



# Auxillary functions for getting GPS and SH data
def get_spec(inFile):
    # Reads in spectrum from get_sh_spectra.c output
    # Declare global variables for editing
    global peak_chan,freqs

    if inFile == '':
        lines = open(opts.spec).readlines()
    else: # Used for non-realtime functions
        lines = open(inFile).readlines()
    if len(lines) != 0: # Continue if the file has data
        if len(freqs) ==0: # Assign frequencies and peak_chan if not assigned
            freqs = np.array(map(float,lines[1].rstrip('\n').split(',')[1:]))
            peak_chan = np.argmax(freqs == opts.freq) # Get index of opts.freq for gridding
            freqs = freqs[peak_chan-10:peak_chan+10] # opts.freq is freqs[10]
        spec_times = [float(line.split(',')[0]) for line in lines[2:] if not line.startswith('#')]
        spec_raw = [map(float,line.rstrip('\n').split(',')[peak_chan-10:peak_chan+10]) for line in lines[2:]\
                            if not line.startswith('#')] # channel for opts.freq is spec_raw[i,10]
        return np.array(spec_times),np.array(spec_raw)

def get_gps(inFile):
    # Reads in gps data from ECHO_Get_GPS.py
    lines = open(inFile).readlines()
    gps_raw = [map(float,line.rstrip('\n').split(',')) for line  in lines if not line.startswith('#')]
    return np.array(gps_raw)



# Initialize outfile
start_timestr = time.strftime('%H:%M:%S')
start_datestr = time.strftime('%d_%m_%Y')
outfile_str = 'accumulated_'+start_datestr+'_'+start_timestr+'.txt'
headstr = '# Accumulated data for '+start_datestr+', '+start_timestr
colfmtstr = '# Column Format: 0 Time [GPS s], 1 Lat [deg], 2 Lon [deg],\
                     3 Rel Alt [m], 4:end Radio Spectrum'
with open(outfile_str,'ab') as outfile:
    outfile.write(headstr+'\n'+colfmtstr+'\n')

# GPS interpolation function
from scipy.interpolate import interp1d
def interp(gps):
    lati = interp1d(gps[:,0],gps[:,1],kind='zero')
    loni = interp1d(gps[:,0],gps[:,2],kind='zero')
    alti = interp1d(gps[:,0],gps[:,3],kind='zero')
    return lati,loni,alti



# Stitches together two seperate GPS and SH files
else:
    # Read in GPS data
    for inFile in args:
        if 'gps' in inFile:
            # Extract GPS information
            gps_raw = get_gps(inFile)
        if 'sh' in inFile:
            # Extract SH spectrum
            spec_times,spec_raw = get_spec(inFile)
            for i in range(0,spec_times.shape[0]):
                spec_times[i] = Time(spec_times[i],scale='utc',format='unix').gps

    #Obtain minimum and maximum times for Interpolation
    #Necessary to avoid interpolation range errors
    minTime = np.max([gps_raw[:,0].min(),spec_times.min()])
    maxTime = np.min([gps_raw[:,0].max(),spec_times.max()])

    #print minTime,maxTime
    #print gps_raw[:,0].min(),gps_raw[:,0].max()
    #print spec_times.min(),spec_times.max()
    #print spec_times.shape

    #Obtain times from Orbcomm data that lie in the time range of the APM data
    timeIndices = np.where(np.logical_and(spec_times>minTime,spec_times<maxTime))[0]
    spec_times,spec_raw = (spec_times[timeIndices],spec_raw[timeIndices,:])
    #print spec_times.shape

    # Interpolate GPS data
    lati,loni,alti = interp(gps_raw)
    if spec_times.shape[0] > 0:
        lats,lons,alts = lati(spec_times),loni(spec_times),alti(spec_times)
    else:
        print '\nNo valid spectrum file to read in\nExiting...\n'
        sys.exit()

    # Make all_data array with interpolated gps positions
    for i in range(0,spec_times.shape[0]):
        all_Data.append([spec_times[i],lats[i],lons[i],alts[i],spec_raw[i,:]])







'''##########################################
                    From ECHO_plot.py
##########################################'''


# Reading functions
def get_data(infile,filetype=None,freqs=[],freq_chan=None):
    if filetype == 'gps':
        gps_arr = []
        lines = open(infile).readlines()
        count = len(lines)
        gps_arr = [map(float,line.rstrip('\n').split(',')) for line in lines[2:] if len(line.split(','))==4]
        return np.array(gps_arr)

    elif filetype == 'sh':
        spec_times = []
        spec_raw = []
        lines = open(infile).readlines()
        count = len(lines)
        if count != 0:
            if len(freqs) == 0:
                freqs = np.array(map(float,lines[1].rstrip('\n').split(',')[1:]))
                freq_chan = np.argmax(freqs == opts.freq) # Get index of opts.freq for gridding
                freqs = freqs[freq_chan-10:freq_chan+10] # opts.freq is freqs[10]
            for line in lines:
                if line.startswith('#'):
                    continue
                line = line.rstrip('\n').split(',')
                if len(line) == 4097: # Make sure line has finished printing
                    spec_times.append(float(line[0]))
                    spec_raw.append(map(float,line[freq_chan-10:freq_chan+10]))
        return np.array(spec_times),np.array(spec_raw),np.array(freqs),freq_chan

    elif filetype == 'echo':
        all_Data = []
        freqs = []
        #print '\nReading in %s...' %inFile
        lines = open(infile).readlines()
        # Add information from flight to all_Data array
        if not 'transmitter' in infile:
            lat0,lon0 = map(float,lines[2].rstrip('\n').split(':')[1].strip(' ').split(','))
            freqs = map(float,lines[3].rstrip('\n').split(':')[1].strip(' ').split(','))
            freqs = np.array(freqs)
        for line in lines[4:]: # Data begins on fifth line of accumulated file
            if line.startswith('#'):
                continue
            elif not line.split(',')[1] == '-1':
                    all_Data.append(map(float,line.rstrip('\n').split(',')))
        all_Data = np.array(all_Data)
        #print 'Converted to array with shape %s and type %s' %(all_Data.shape,all_Data.dtype)
        # Extract information from all_Data array
        if 'transmitter' in infile: # Green Bank data
            spec_times,lats,lons,alts = (all_Data[:,1],all_Data[:,2],all_Data[:,3],all_Data[:,4])
            if 'Nant' in infile:
                lat0,lon0 = (38.4248532,-79.8503723)
                if 'NS' in infile:
                    spec_raw = all_Data[:,12:17] # N antenna, NS dipole
                if 'EW' in infile:
                    spec_raw = all_Data[:,24:29] # N antenna, EW dipole
            if 'Sant' in infile:
                lat0,lon0 = (38.4239235,-79.8503418)
                if 'NS' in infile:
                    spec_raw = all_Data[:,6:11] # S antenna, NS dipole
                if 'EW' in infile:
                    spec_raw = all_Data[:,18:23] # S antenna, EW dipole
        else:
            spec_times,lats,lons,alts,spec_raw = (all_Data[:,0],all_Data[:,1],all_Data[:,2],\
                                                                        all_Data[:,3],all_Data[:,4:])
        return spec_times,spec_raw,freqs,lats,lons,alts,lat0,lon0

    else:
        print '\nNo valid filetype found for %s' %infile
        print 'Exiting...\n\n'
        sys.exit()



# Time functions
def find_peak(f,x,fmin=0,fmax=500):
    # f = frequencies in MHz
    # x = spectrum
    # fmin,fmax range in which to search for peak
    fchans = np.argwhere(np.logical_and(f>fmin,f<fmax))
    peak = x[fchans].max()
    maxfreq = f[fchans[x[fchans].argmax()]]
    peakrms = np.mean(x[fchans.max():fchans.max()+100])
    return maxfreq,peak,peakrms


# Position functions
def latlon2xy(lat,lon,lat0,lon0):
    x = r_earth*(lon - lon0)*(np.pi/180)
    y = r_earth*(lat - lat0)*(np.pi/180)
    return x,y

def to_spherical(x,y,z):
    # x and y are cartesian coordinates
    # z is relative altitude
    rhos = np.sqrt(x**2+y**2+z**2)
    thetas = np.arccos(z/rhos) # Zentih angle
    phis = np.arctan2(y,x) # Azimuthal angle
    return rhos,thetas,phis



# Server API functions


# Plotting functions
def make_beam(lats,lons,alts,spec_raw,lat0=0.0,lon0=0.0,volts=False):
    # Convert lat/lon to x/y
    if opts.lat0 and opts.lon0:
        x,y = latlon2xy(lats,lons,opts.lat0,opts.lon0)
    else:
        x,y = latlon2xy(lats,lons,lat0,lon0)
    # Obtain spherical coordinates for x, y, and alt
    rs,thetas,phis = to_spherical(x,y,alts)

    # z (power) will set color value for gridded data
    #freqIndex = np.argmax(spec_raw[0,:])
    freqIndex = 10
    # Only extract information from appropriate column (index = 10)
    z = spec_raw[:,freqIndex]
    if volts:
        # Distance normalization
        r0 = 100 # reference position for distance normalization (unit: meters)
        z = 10*np.log10((2*z**2)*(rs/r0)**2)
        # log(V^2) -> dB
    # Normalize for plotting [-inf,0]
    z -= z.max()

    # Set binsize (used in function grid_data)
    # Affects the apparent size of the pixels on the plot created below.
    binsize=5
    # Obtain gridded data
    grid,bins,rmsBins,binloc,xg,yg,gcounts,grms = grid_data(x,y,z,binsize=binsize)

    # Healpix things
    nsides = opts.nsides
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
    hpx_beam[hpx_beam == 0] = np.nan
    hpx_counts[hpx_counts == 0] = np.nan
    hpx_rms[hpx_rms == 0] = np.nan

    return hpx_beam,hpx_counts,hpx_rms

def grid_data(x, y, z, binsize=0.01, retbin=True, retloc=True, retrms=True):
    # Get extrema values.
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()
    # Make coordinate arrays.
    xi = np.arange(xmin, xmax+binsize, binsize)
    yi = np.arange(ymin, ymax+binsize, binsize)
    xi, yi = np.meshgrid(xi,yi)

    # Make the grid.
    grid = np.zeros(xi.shape, dtype=x.dtype)
    nrow, ncol = grid.shape
    if retbin: bins = np.copy(grid)
    if retrms: rmsBins = np.copy(grid)

    # Make arrays to store counts/rms for Healpix data
    gcounts = np.zeros_like(z)
    grms = np.zeros_like(z)

    # Create list in same shape as grid to store indices
    if retloc:
        wherebin = np.copy(grid)
        wherebin = wherebin.tolist()
    # Fill in the grid.
    for row in range(nrow):
        for col in range(ncol):
            xc = xi[row, col]    # x coordinate.
            yc = yi[row, col]    # y coordinate.

            # Find the position that xc and yc correspond to.
            posx = np.abs(x - xc)
            posy = np.abs(y - yc)
            ibin = np.logical_and(posx < binsize/2., posy < binsize/2.)
            ind  = np.where(ibin == True)[0]

            # Fill the bin.
            bin = z[ibin]
            gcounts[ibin] = np.sum(ibin) # Update counts at each x position
            if retloc: wherebin[row][col] = ind
            if retbin: bins[row, col] = bin.size
            if bin.size != 0:
                binval = np.median(bin)
                grid[row, col] = binval
                if retrms:
                    rmsBins[row,col] = np.std(bin)
                    grms[ibin] = np.std(bin)
            else:
                grid[row, col] = np.nan   # Fill empty bins with nans.
                if retrms:
                    rmsBins[row,col] = np.nan
                    grms[ibin] = np.nan

    # Return the grid
    if retbin:
        if retloc:
            if retrms:
                return np.ma.masked_invalid(grid), bins, np.ma.masked_invalid(rmsBins),\
                            wherebin, xi, yi, gcounts, grms
            else:
                return np.ma.masked_invalid(grid), bins, wherebin, xi, yi, gcounts, grms
        else:
            return np.ma.masked_invalid(grid), bins, xi, yi, gcounts, grms
    else:
        if retloc:
            if retrms:
                return np.ma.masked_invalid(grid), np.ma.masked_invalid(rmsBins),\
                            wherebin, xi, yi, gcounts, grms
            else:
                return np.ma.masked_invalid(grid), wherebin, xi, yi, gcounts, grms
        else:
            if retrms:
                return np.ma.masked_invalid(grid), np.ma.masked_invalid(rmsBins),\
                            xi, yi, gcounts, grms
            else:
                return np.ma.masked_invalid(grid), xi, yi, gcounts, grms


def animate_spectrum(i,spec_line,spec_raw):
    spec_line.set_ydata(spec_raw[i,:])
    return

def animate_peak(i,peak_plot,peak_line,spec_times,spec_raw,peaktimes,peakvals,\
                           peakfreqs,rmss,peakrmss,freqs,fmin,fmax,rmswindow=10):
    currtime = spec_times[i]
    if currtime == peaktimes[-1]:
        return
    peakfreq,peakval,rms = find_peak(freqs,spec_raw[i,:],fmin=fmin,fmax=fmax)
    peaktimes.append(currtime)
    peakvals.append(peakval)
    peakfreqs.append(peakfreq)
	rmss.append(rms)
	if len(peakvals)<rmswindow:
	    peakrmss.append(np.std(peakvals))
    else:
        peakrmss.append(np.std(peakvals[-rmswindow:]))

    # Update peak plot
    peak_line.set_xdata(peaktimes)
    peak_line.set_ydata(peakvals)
    peak_plot.relim()
    peak_plot.autoscale_view(True,True,True)
    peak_plot.set_xlim([currtime-time_range,currtime])
    noise_line.set_xdata(peaktimes)
    noise_line.set_ydata(rmss)

    # Update peak RMS plot
    pkrms_line.set_xdata(peaktimes)
    pkrms_line.set_ydata(peakrmss)
    pkrms_plot.relim()
    pkrms_plot.set_xlim([currtime-time_range,currtime])
    pkrms_plot.autoscale_view(True,True,True)
    return

def animate_beam(beam_plot,hpx_beam):
    pix = np.argwhere(np.isnan(hpx_beam)==False).squeeze()
    boundaries = hp.boundaries(opts.nsides,pix)
    verts = np.swapaxes(boundaries[:,0:2,:],1,2)
    coll = PolyCollection(verts, array=hpx_beam[np.isnan(hpx_beam)==False],\
                                    cmap=cm.gnuplot,edgecolors='none')
    beam_plot.collections.remove(beam_plot.collections[-1])
    beam_plot.add_collection(coll)

def adjustErrbarxy(errobj, x, y, y_error):
    # http://stackoverflow.com/questions/25210723/matplotlib-set-data-for-errorbar-plot
    ln, (erry_top, erry_bot), barsy = errobj
    x_base = x
    y_base = y
    ln.set_ydata(y)
    yerr_top = y_base + y_error
    yerr_bot = y_base - y_error
    erry_top.set_ydata(yerr_top)
    erry_bot.set_ydata(yerr_bot)
    new_segments_y = [np.array([[x, yt], [x,yb]]) for x, yt, yb in zip(x_base, yerr_top, yerr_bot)]
    barsy[0].set_segments(new_segments_y)

def animate_cuts(cuts_E_line,cuts_H_line,hpx_beam,ell,az):
    beam_slice_E = hp.pixelfunc.get_interp_val(hpx_beam,ell,az)
    beam_slice_E_err = hp.pixelfunc.get_interp_val(hpx_rms,ell,az)
    beam_slice_H = hp.pixelfunc.get_interp_val(hpx_beam,ell,az+np.pi/2)
    beam_slice_H_err = hp.pixelfunc.get_interp_val(hpx_rms,ell,az+np.pi/2)

    adjustErrbarxy(cuts_E_line,ell,beam_slice_E,beam_slice_E_err)
    adjustErrbarxy(cuts_H_line,ell,beam_slice_H,beam_slice_H_err)
