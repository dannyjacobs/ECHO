'''

    Author: Jacob Burba

    ECHO_plot.py does useful things for some and pointless things for others.  Such is life.

'''


from matplotlib import cm,use
use('TkAgg')
from matplotlib.collections import PolyCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable
from astropy.time import Time

import urllib2,optparse,sys,json,time,warnings
import numpy as np
import healpy as hp
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt


'''####################################################
#                                                OPTION PARSER                                               #
####################################################'''

o = optparse.OptionParser()
o.set_description('Queries ground station server for interpolated GPS position')
o.add_option('--acc_file',type=str,help='Accumulated file for plotting')
o.add_option('--nsides',type=int,default=8,help='Number of sides for Healpix plotting (Default = 8)')
o.add_option('--realtime',action='store_true',help='Specify realtime or not')
o.add_option('--lat0',type=float,help='Latitude of antenna under test')
o.add_option('--lon0',type=float,help='Longitude of antenna under test')
o.add_option('--freq',type=float,help='Peak frequency to look for in data')
opts,args = o.parse_args(sys.argv[1:])


'''####################################################
#                                             GLOBAL FUNCTIONS                                            #
####################################################'''

def get_data(inFile):
    # Read in preprocessed file
    # The first two lines contain comment and formatting information
    # Skip first 2 lines, 3rd line contains lat0 and lon0
    # Column format is: 0 Time [gps s], 1 lat [deg], 2 lon [deg], 3 alt [m], 4:end spectrum (dB)

    all_Data = []
    freqs = []
    print 'Reading in %s...' %inFile
    lines = open(inFile).readlines()
    # Add information from flight to all_Data array
    if not 'transmitter' in inFile:
        lat0,lon0 = map(float,lines[2].strip('\n').split(':')[1].strip(' ').split(','))
        freqs = map(float,lines[3].strip('\n').split(':')[1].strip(' ').split(','))
    for line in lines[4:]: # Data begins on fifth line of accumulated file
        all_Data.append(map(float,line.strip('\n').split(',')))

    all_Data = np.array(all_Data)
    print 'Converted to array with shape %s and type %s' %(all_Data.shape,all_Data.dtype)
    # Extract information from all_Data array
    if 'transmitter' in inFile: # Green Bank data
        spec_times,lats,lons,alts = (all_Data[:,1],all_Data[:,2],all_Data[:,3],all_Data[:,4])
        if 'Nant_NS' in inFile: spec_raw = all_Data[:,12:17] # N antenna, NS dipole
        if 'Nant_EW' in inFile: spec_raw = all_Data[:,24:29] # N antenna, EW dipole
        if 'Sant_NS' in inFile: spec_raw = all_Data[:,6:11] # S antenna, NS dipole
        if 'Sant_EW' in inFile: spec_raw = all_Data[:,18:23] # S antenna, EW dipole
    else:
        spec_times,lats,lons,alts,spec_raw = (all_Data[:,0],all_Data[:,1],all_Data[:,2],\
                                                                    all_Data[:,3],all_Data[:,4:])
    return all_Data,spec_times,spec_raw,lats,lons,alts
# End get_data


def griddata(x, y, z, binsize=0.01, retbin=True, retloc=True, retrms=True):
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
# End griddata


def make_beam(lats,lons,alts,spec_raw,lat0=0,lon0=0):

    # Convert lat/lon to x/y
    if opts.lat0 and opts.lon0:
        x,y = latlon2xy(lats,lons,opts.lat0,opts.lon0)
    else:
        x,y = latlon2xy(lats,lons,lat0,lon0)
    # Obtain spherical coordinates for x, y, and alt
    rs,thetas,phis = to_spherical(x,y,alts)

    # z (power) will set color value for gridded data
    freqIndex = np.argmax(spec_raw[0,:])
    # Only extract information from appropriate column (index = 10)
    z = spec_raw[:,freqIndex]
    # Distance normalization
    r0 = 100 # reference position for distance normalization (unit: meters)
    z = np.log10((2*z**2)*(rs/r0)**2)
    # log(V^2) -> dB and normalization for healpix plotting range [-inf,0]
    z = 10*(z-z.max())

    # Set binsize (used in function griddata)
    # Affects the apparent size of the pixels on the plot created below.
    binsize=5
    # Obtain gridded data
    grid,bins,rmsBins,binloc,xg,yg,gcounts,grms = griddata(x,y,z,binsize=binsize)
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
# End make_beam


def latlon2xy(lat,lon,lat0,lon0):
    x = r_earth*(lon - lon0)*(np.pi/180)
    y = r_earth*(lat - lat0)*(np.pi/180)
    return x,y
# End latlon2xy


def to_spherical(x,y,z):
    # x and y are cartesian coordinates
    # z is relative altitude
    rhos = np.sqrt(x**2+y**2+z**2)
    thetas = np.arccos(z/rhos) # Zentih angle
    phis = np.arctan2(y,x) # Azimuthal angle
    return rhos,thetas,phis
# End to_spherical


# Declare constants
i = 0
r_earth = 6371000 # meters

'''####################################################
#                                                   REALTIME                                                     #
####################################################'''

if opts.realtime: # Realtime mapping and data

    def find_peak(f,x,fmin=0,fmax=500):
        # f = frequencies in MHz
        # x = spectrum
        # fmin,fmax range in which to search for peak
        fchans = np.argwhere(np.logical_and(f>fmin,f<fmax))
        peak = x[fchans].max()
        maxfreq = f[fchans[x[fchans].argmax()]]
        peakrms = np.mean(x[fchans.max():fchans.max()+100])
        return maxfreq,peak,peakrms
    # End find_peak


    def animate_spectrum(i):
        spec_line.set_ydata(spec_raw[i,:])
        return
    # End animate_spectrum


    def animate_peak(i):
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
    # End animate_peak


    def animate_beam(coll):
        hpx_beam,hpx_counts,hpx_rms = make_beam(lats,lons,alts,spec_raw)
        coll.set_array(hpx_beam[np.isnan(hpx_beam)==False])
    # End animate_beam


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
    # End adjustErrbarxy

    def animate_cuts():
        beam_slice_E = hp.pixelfunc.get_interp_val(hpx_beam,alt,az)
        beam_slice_E_err = hp.pixelfunc.get_interp_val(hpx_rms,alt,az)
        beam_slice_H = hp.pixelfunc.get_interp_val(hpx_beam,alt,az+np.pi/2)
        beam_slice_H_err = hp.pixelfunc.get_interp_val(hpx_rms,alt,az+np.pi/2)

        adjustErrbarxy(cuts_E_line,ell,beam_slice_E,beam_slice_E_err)
        adjustErrbarxy(cuts_H_line,ell,beam_slice_H,beam_slice_H_err)
    # End animate_cuts


    fmin,fmax = int(opts.freq)-1,int(opts.freq)+1 # MHz; for plotting
    time_range = 200 # Time range in seconds of peak plot window
    rmswindow = 10

    # Get initial data from Signal Hound
    all_Data,spec_times,spec_raw,lats,lons,alts = get_data(opts.acc_file)
    if spec_times.shape[0] == 0: # Ensure data in inFile
        print 'Invalid data: array with zero dimension\nExiting...\n'
        sys.exit()

    # Initialize plotting figure
    fig = plt.figure(dpi=80,facecolor='w',edgecolor='w') # figsize=(16,9))
    mng = plt.get_current_fig_manager() # Make figure full screen
    # Make background subplot for title for all plots
    ax = fig.add_subplot(111)
    ax.set_title(r'Real-time ECHO Stuff',y=1.08,size=16)
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')

    # Spectrum plot initialization
    gs1 = gridspec.GridSpec(3, 1) # Sets up grid for placing plots
    spec_plot = fig.add_subplot(gs1[0]) # Initialize the spectrum plot in figure
    spec_line, = spec_plot.plot(freqs,spec_raw[0,:])
    spec_plot.vlines([fmin,fmax],ymin=-100,ymax=10)
    spec_plot.set_xlabel("Frequency [Mhz]")
    spec_plot.set_ylabel("Power [dBm]")
    spec_plot.set_xlim([freqs[0],freqs[-1]])

    # Peak plot initialization
    peak_plot = fig.add_subplot(gs1[1]) # Initialize the peak plot in figure
    peakfreq,peakval,rms = find_peak(freqs,spec_raw[0,:],fmin=fmin,fmax=fmax)
    peaktimes,peakvals,peakfreqs,rmss,peakrmss = [spec_times[0]],[peakval],[peakfreq],[rms],[0]
    peak_line, = peak_plot.plot(peaktimes,peakvals,label='Peak')
    noise_line, = peak_plot.plot(peaktimes,rmss,'k',label='Noise')
    peak_plot.autoscale_view(True,True,True) # Autoscale for changes in RMS
    peak_plot.set_xlabel('Time [s]')
    peak_plot.set_ylabel('Peak Power [dBm]')
    peak_plot.legend(loc='upper left')

    # Peak rms plot initialization
    pkrms_plot = fig.add_subplot(gs1[2])
    pkrms_line,= pkrms_plot.plot(peaktimes,peakrmss,'k',label='Peak Variability')
    pkrms_plot.set_xlabel('Time [s]')
    pkrms_plot.set_ylabel('Peak RMS [dB]')
    pkrms_plot.legend(loc='upper left')

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        # This raises warnings since tight layout cannot
        # handle gridspec automatically. We are going to
        # do that manually so we can filter the warning.
        gs1.tight_layout(fig, rect=[0, 0, 0.5, 1])


    # Make beam, counts, and rms from gridded data
    # griddata(...) called in make_beam(...)
    hpx_beam,hpx_counts,hpx_rms = make_beam(lats,lons,alts,spec_raw)

    # Cuts and beam plot initializations
    gs2 = gridspec.GridSpec(2, 1,height_ratios=[1,2])
    plot_lim = [-40,5]

    # Beam plot initialization
    gs = gridspec.GridSpec(1, 2) # Sets up grid for placing plots
    beam_plot = fig.add_subplot(gs[0],aspect='equal')

    pix = np.argwhere(np.isnan(hpx_beam)==False).squeeze()
    boundaries = hp.boundaries(opts.nsides,pix)
    verts = np.swapaxes(boundaries[:,0:2,:],1,2)
    coll, = PolyCollection(verts, array=hpx_beam[np.isnan(hpx_beam)==False],\
                                    cmap=cm.gnuplot,edgecolors='none')
    coll.set_clim(plot_lim)
    beam_plot.add_collection(coll)
    beam_plot.autoscale_view()

    # Position colorbar next to plot with same height as plot
    divider = make_axes_locatable(beam_plot)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(coll, cax=cax, use_gridspec=True, label='dB') # orientation='horizontal')

    for radius_deg in [20,40,60,80]:
        r = np.sin(radius_deg*np.pi/180.)
        x = np.linspace(-r,r,100)
        beam_plot.plot(x,np.sqrt(r**2-x**2),'w-',linewidth=3)
        beam_plot.plot(x,-np.sqrt(r**2-x**2),'w-',linewidth=3)

    # Cuts plot initialization
    cuts_plot = fig.add_subplot(gs[1])

    #receiver coordinates
    ell = np.linspace(-np.pi/2,np.pi/2)
    az = np.zeros_like(ell)
    xticks = [-90,-60,-40,-20,0,20,40,60,90]
    beam_slice_E = hp.pixelfunc.get_interp_val(hpx_beam,ell,az) #- tx_beam
    beam_slice_E_err = hp.pixelfunc.get_interp_val(hpx_rms,ell,az)
    beam_slice_H = hp.pixelfunc.get_interp_val(hpx_beam,ell,az+np.pi/2) #- tx_beam
    beam_slice_H_err = hp.pixelfunc.get_interp_val(hpx_rms,ell,az+np.pi/2)

    cuts_E_line = cuts_plot.errorbar(ell*180/np.pi,beam_slice_E,beam_slice_E_err,fmt='b.',label='ECHO [E]')
    cuts_H_line = cuts_plot.errorbar(ell*180/np.pi,beam_slice_H,beam_slice_H_err,fmt='r.',label='ECHO [H]')
    cuts_plot.legend(loc='best')
    cuts_plot.set_ylabel('dB')
    cuts_plot.set_xlabel('Elevation Angle [deg]')
    cuts_plot.set_xlim([-95,95])
    cuts_plot.set_xticks(xticks)
    cuts_plot.set_ylim(plot_lim)

    with warnings.catch_warnings():
        # This raises warnings since tight layout cannot
        # handle gridspec automatically. We are going to
        # do that manually so we can filter the warning.
        warnings.simplefilter("ignore", UserWarning)
        gs2.tight_layout(fig, rect=[0.5, None, None, None])

    mng.window.state('zoomed')
    plt.draw()
    plt.show(block=False)

    try:
        while True:
            while i < spec_times.shape[0]:
                # Update plotting window
                animate_spectrum(i)
                animate_peak(i)
                animate_beam(coll)
                animate_cuts()
                plt.draw()
                #plt.show(block=False)
                i = i+1

            # Get updated data from Signal Hound
            all_Data,spec_times,spec_raw,lats,lons,alts = get_data(opts.acc_file)
    except KeyboardInterrupt:
        print 'Exiting...\n'
        sys.exit()




    '''####################################################
    #                                                NOT REALTIME                                                 #
    ####################################################'''

    '''

            All code in this section works for Green Bank combined files.
            Needs to be tested on an accumulated text file.

    '''

else:

    # Initialize array to store data
    all_Data,spec_times,spec_raw,lats,lons,alts = get_data(opts.acc_file)
    hpx_beam,hpx_counts,hpx_rms = make_beam(lats,lons,alts,spec_raw)

    # Initialize plotting figure
    fig = plt.figure(figsize=(16,9),dpi=80,facecolor='w',edgecolor='w')
    mng = plt.get_current_fig_manager() # Make figure full screen
    plot_lim = [-40,5]
    ax = fig.add_subplot(111)
    ax.set_title(r'ECHO Stuff is WORKING',y=1.08,size=16)
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')

    # Beam plot initialization
    gs = gridspec.GridSpec(1, 2) # Sets up grid for placing plots
    beam_plot = fig.add_subplot(gs[0],aspect='equal')

    pix = np.argwhere(np.isnan(hpx_beam)==False).squeeze()
    boundaries = hp.boundaries(opts.nsides,pix)
    verts = np.swapaxes(boundaries[:,0:2,:],1,2)
    coll = PolyCollection(verts, array=hpx_beam[np.isnan(hpx_beam)==False],\
                                    cmap=cm.gnuplot,edgecolors='none')
    coll.set_clim(plot_lim)
    beam_plot.add_collection(coll)
    beam_plot.autoscale_view()

    # Position colorbar next to plot with same height as plot
    divider = make_axes_locatable(beam_plot)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(coll, cax=cax, use_gridspec=True, label='dB') # orientation='horizontal')

    for radius_deg in [20,40,60,80]:
        r = np.sin(radius_deg*np.pi/180.)
        x = np.linspace(-r,r,100)
        beam_plot.plot(x,np.sqrt(r**2-x**2),'w-',linewidth=3)
        beam_plot.plot(x,-np.sqrt(r**2-x**2),'w-',linewidth=3)

    # Cuts plot initialization
    cuts_plot = fig.add_subplot(gs[1])

    #receiver coordinates
    ell = np.linspace(-np.pi/2,np.pi/2)
    az = np.zeros_like(ell)
    xticks = [-90,-60,-40,-20,0,20,40,60,90]
    beam_slice_E = hp.pixelfunc.get_interp_val(hpx_beam,ell,az) #- tx_beam
    beam_slice_E_err = hp.pixelfunc.get_interp_val(hpx_rms,ell,az)
    beam_slice_H = hp.pixelfunc.get_interp_val(hpx_beam,ell,az+np.pi/2) #- tx_beam
    beam_slice_H_err = hp.pixelfunc.get_interp_val(hpx_rms,ell,az+np.pi/2)

    cuts_plot.errorbar(ell*180/np.pi,beam_slice_E,beam_slice_E_err,fmt='b.',label='ECHO [E]')
    cuts_plot.errorbar(ell*180/np.pi,beam_slice_H,beam_slice_H_err,fmt='r.',label='ECHO [H]')
    cuts_plot.legend(loc='best')
    cuts_plot.set_ylabel('dB')
    cuts_plot.set_xlabel('Elevation Angle [deg]')
    cuts_plot.set_xlim([-95,95])
    cuts_plot.set_xticks(xticks)
    cuts_plot.set_ylim(plot_lim)

    '''
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        # This raises warnings since tight layout cannot
        # handle gridspec automatically. We are going to
        # do that manually so we can filter the warning.
        gs.tight_layout(fig, rect=[0, 0, 1, 1],h_pad=0.2)
    '''

    # Show plot window
    plt.subplots_adjust(wspace=0.5)
    mng.window.state('zoomed')
    plt.show()




    '''
    ########################## EXILED CODE #############################


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

    '''
