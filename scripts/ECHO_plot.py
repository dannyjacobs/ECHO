'''

    Author: Jacob Burba

    ECHO_plot.py does useful things for some and pointless things for others.  Such is life.
    --lat0 and --lon0 optional

'''

#from matplotlib import use
#use('TkAgg')
from mpl_toolkits.axes_grid1 import make_axes_locatable
import ECHO_read_utils
from ECHO_read_utils import get_data

print ECHO_read_utils.__file__

from ECHO_position_utils import *

import urllib2,optparse,sys,json,time,warnings
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt


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
#                    REALTIME                         #
####################################################'''

if opts.realtime:

    from ECHO_time_utils import find_peak
    from ECHO_plot_utils import *

    fmin,fmax = int(opts.freq)-1,int(opts.freq)+1 # MHz; for plotting
    time_range = 200 # Time range in seconds of peak plot window
    rmswindow = 10

    # Get initial data from Signal Hound
    spec_times,spec_raw,freqs,lats,lons,alts,lat0,lon0 = get_data(opts.acc_file,filetype='echo',freq=137.500)
    print freqs
    #print freqs.shape,spec_raw.shape
    if spec_times.shape[0] == 0: # Ensure data in inFile
        print 'Invalid data: array with zero dimension\nExiting...\n'
        sys.exit()

    # Initialize plotting figure
    fig = plt.figure(figsize=(16,9),dpi=80,facecolor='w',edgecolor='w')
    #mng = plt.get_current_fig_manager() # Make figure full screen
    fig.suptitle('ECHO Realtime Data Visualization for %s' %opts.acc_file,fontsize=16)

    # Spectrum plot initialization
    gsl = gridspec.GridSpec(2,1) # Sets up grid for placing plots
    spec_plot = fig.add_subplot(gsl[0]) # Initialize the spectrum plot in figure
    spec_line, = spec_plot.plot(freqs,spec_raw[0,:])
    #freq_labels = [freqs[0],freqs[9],freqs[10],freqs[11],freqs[-1]]
    #plt.xticks(freq_labels,map(str,freq_labels),rotation=45)
    spec_plot.set_xlabel("Frequency [Mhz]")
    spec_plot.set_ylabel("Power [dBm]")
    spec_plot.grid()
    spec_plot.axvline(x=opts.freq)
    #spec_plot.set_ylim([-90,10])
    #spec_plot.set_xlim([freqs[0],freqs[-1]])

    # Peak plot initialization
    gsl_lower_cell = gsl[1]
    gsl_lower_grid = gridspec.GridSpecFromSubplotSpec(2,1,gsl_lower_cell,hspace=0.0)
    peak_plot = fig.add_subplot(gsl_lower_grid[0]) # Initialize the peak plot in figure
    peakfreq,peakval,rms = find_peak(freqs,spec_raw[0,:],fmin=fmin,fmax=fmax)
    peaktimes,peakvals,peakfreqs,rmss,peakrmss = [spec_times[0]],[peakval],[peakfreq],[rms],[0]
    peak_line, = peak_plot.plot(peaktimes,peakvals,label='Peak')
    noise_line, = peak_plot.plot(peaktimes,rmss,'k',label='Noise')
    peak_plot.set_ylabel('Peak Power [dBm]')
    peak_plot.legend(loc='upper left')
    plt.setp(peak_plot.get_xticklabels(),visible=False)

    # Peak rms plot initialization
    pkrms_plot = fig.add_subplot(gsl_lower_grid[1],sharex=peak_plot)
    pkrms_line,= pkrms_plot.plot(peaktimes,peakrmss,'k',label='Peak Variability')
    pkrms_plot.set_xlabel('Time [H:M:S]')
    pkrms_plot.set_ylabel('Peak RMS [dB]')
    pkrms_plot.legend(loc='upper left')

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        # This raises warnings since tight layout cannot
        # handle gridspec automatically. We are going to
        # do that manually so we can filter the warning.
        gsl.tight_layout(fig, rect=[0, 0, 0.5, 0.97])

    # Make beam, counts, and rms from gridded data
    # grid_data(...) called in make_beam(...)
    if opts.lat0 and opts.lon0:
        lat0,lon0 = opts.lat0,opts.lon0
    hpx_beam,hpx_counts,hpx_rms = make_beam(lats,lons,alts,spec_raw,\
                                      lat0=lat0,lon0=lon0,nsides=opts.nsides)

    # Cuts and beam plot initializations
    gsr = gridspec.GridSpec(2, 1,height_ratios=[1,1])
    plot_lim = [-40,5]

    # Beam plot initialization
    beam_plot = fig.add_subplot(gsr[0],aspect='equal')
    coll = make_polycoll(hpx_beam,nsides=opts.nsides)#,plot_lim=[-90,-50])
    #min_coll = np.nanmin(hpx_beam)
    #max_coll = np.nanmax(hpx_beam)
    #coll.set_clim(plot_lim)
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
    ell = np.linspace(-np.pi/2,np.pi/2)
    az = np.zeros_like(ell)
    xticks = [-90,-60,-40,-20,0,20,40,60,90]
    beam_slice_E = hp.pixelfunc.get_interp_val(hpx_beam,ell,az)
    beam_slice_E_err = hp.pixelfunc.get_interp_val(hpx_rms,ell,az)
    beam_slice_H = hp.pixelfunc.get_interp_val(hpx_beam,ell,az+np.pi/2)
    beam_slice_H_err = hp.pixelfunc.get_interp_val(hpx_rms,ell,az+np.pi/2)

    cuts_E_line = cuts_plot.errorbar(ell*180/np.pi,beam_slice_E,\
                                                    beam_slice_E_err,fmt='b.',label='ECHO [E]')
    cuts_H_line = cuts_plot.errorbar(ell*180/np.pi,beam_slice_H,\
                                                    beam_slice_H_err,fmt='r.',label='ECHO [H]')
    cuts_plot.legend(loc='lower center')
    cuts_plot.set_ylabel('dB')
    cuts_plot.set_xlabel('Elevation Angle [deg]')
    #cuts_plot.set_xlim([-95,95])
    cuts_plot.set_xticks(xticks)
    #cuts_plot.set_ylim([-90,5])

    with warnings.catch_warnings():
        # This raises warnings since tight layout cannot
        # handle gridspec automatically. We are going to
        # do that manually so we can filter the warning.
        warnings.simplefilter("ignore", UserWarning)
        gsr.tight_layout(fig, rect=[0.5, None, None, 0.97])

    plt.subplots_adjust(top=0.8)
    #mng.window.state('zoomed')
    plt.draw()
    plt.show(block=False)

    try:
        plot_ind = 0
        while True:
            # Get updated data from Signal Hound
            spec_times,spec_raw,freqs,lats,lons,alts,lat0,lon0 = get_data(opts.acc_file,filetype='echo',freq=opts.freq)
            hpx_beam,hpx_counts,hpx_rms = make_beam(lats,lons,alts,spec_raw,\
                                                  lat0=lat0,lon0=lon0,nsides=opts.nsides)

            while plot_ind < spec_times.shape[0]:
                # Update plotting window
                animate_spectrum(plot_ind,spec_plot,spec_line,spec_raw)
                animate_peak(plot_ind,peak_plot,peak_line,noise_line,pkrms_plot,pkrms_line,\
                                     spec_times,spec_raw,peaktimes,peakvals,peakfreqs,rmss,\
                            peakrmss,freqs,fmin,fmax,time_range=time_range,rmswindow=rmswindow)
                animate_beam(beam_plot,hpx_beam,fig,cax,cbar,plot_lim=plot_lim,nsides=opts.nsides)
                animate_cuts(cuts_plot,cuts_E_line,cuts_H_line,hpx_beam,hpx_rms,ell,az)
                #fig.canvas.draw()
                plt.pause(0.0001)
                plot_ind += 1

    except KeyboardInterrupt:
        print '\nExiting...\n'
        sys.exit()




    '''####################################################
    #                                                NOT REALTIME                                                 #
    ####################################################'''

    ''' Needs to be edited/fixed '''

else:

    # Initialize array to store data
    spec_times,spec_raw,freqs,lats,lons,alts,lat0,lon0 = get_data(opts.acc_file,filetype='echo')
    hpx_beam,hpx_counts,hpx_rms = make_beam(lats,lons,alts,spec_raw,lat0,lon0)

    # Initialize plotting figure
    fig = plt.figure(figsize=(16,9),dpi=80,facecolor='w',edgecolor='w')
    #mng = plt.get_current_fig_manager() # Make figure full screen
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

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        # This raises warnings since tight layout cannot
        # handle gridspec automatically. We are going to
        # do that manually so we can filter the warning.
        gs.tight_layout(fig, rect=[0, 0, 1, 1],h_pad=0.2)

    # Show plot window
    plt.subplots_adjust(wspace=0.5)
    #mng.window.state('zoomed')
    plt.show()
