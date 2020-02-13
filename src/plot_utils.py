import numpy as np,os,sys
import healpy as hp
import math
from healpy import _healpy_pixel_lib as pixlib
from matplotlib.collections import PolyCollection
from matplotlib import cm,colors
import matplotlib.pyplot as plt
from matplotlib._png import read_png

from position_utils import latlon2xy,to_spherical
from time_utils import gps_to_HMS,find_peak

def cmap_discretize(cmap, N):
    """Return a discrete colormap from the continuous colormap cmap.

        cmap: colormap instance, eg. cm.jet.
        N: number of colors.

    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)

    borrowed from
    http://scipy.github.io/old-wiki/pages/Cookbook/Matplotlib/ColormapTransformations
    """

    if type(cmap) == str:
        cmap = cm.get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N+1)
    cdict = {}
    for ki,key in enumerate(('red','green','blue')):
        cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki]) for i in xrange(N+1) ]
    # Return colormap object.
    return colors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)

class nf(float):
    def __repr__(self):
        str = '%.1f' % (self.__float__(),)
        if str[-1] == '0':
            return '%.0f' % self.__float__()
        else:
            return '%.1f' % self.__float__()
fmt = '%r$^\circ$'

def rotate_hpm(hpm,rot_phi,rot_theta,pol='EW'):
    """rotate hpm about phi, then theta (degrees)
    if pol=EW theta is rotated about the X axis (default)
    if pol=NS theta is rotated about the Y axis
    """
    nside = hp.npix2nside(len(hpm))
    indexes = np.arange(len(hpm))
    theta,phi = hp.pix2ang(nside,indexes)      #get the input map angles (rad)
    if pol=='NS':
        eulertype='X'
    else:
        eulertype='Y'
    R = hp.rotator.Rotator(rot=(rot_phi,rot_theta),deg=True,eulertype=eulertype)                  #make the rotator
    rotated_theta,rotated_phi = R(theta,phi) #rotate new radians
    return get_interp_val(hpm,rotated_theta,rotated_phi)


def rotate_hpm_old(hpm,angle,theta_angle=0):
    "rotate hpm angle degrees around the zero pixel (ie around the north pole)"
    "Optionally apply a second rotation of theta degrees in the new phi=0 plane"
    nside = hp.npix2nside(len(hpm))
    indexes = np.arange(len(hpm))
    theta,phi = hp.pix2ang(nside,indexes)      #get the input map angles
    #interpolate to a higher nside, rotate that thing
    interp_map = hp.ud_grade(hpm,nside*2)
    theta_interp,phi_interp = hp.pix2ang(nside*2,np.arange(len(hpm)*4))
    phi_interp += angle*np.pi/180  #apply the azimuthal rotation
    #get the rotated interpolated map
    rotated_interpolated_beam = get_interp_val(hpm,theta_interp,phi_interp)
    #interpolate back to the original map pixels
    rotated_hpm = get_interp_val(rotated_interpolated_beam,theta,phi)
    if theta_angle!=0:
        theta_interp,phi_interp = hp.pix2ang(nside*2,np.arange(len(hpm)*4))
        theta_interp += theta_angle*np.pi/180 * np.cos(phi_interp)
        rotated_interpolated_beam = get_interp_val(rotated_hpm,theta_interp,phi_interp)
        rotated_hpm = get_interp_val(rotated_interpolated_beam,theta,phi)
    return rotated_hpm

def project_healpix(M,rotate_angle=0):
    #flat plotting
    try:
        M.mask
    except(AttributeError):
        M = np.ma.array(M)
    xmax = 1#np.sin(theta.max())
    X,Y = np.meshgrid(np.linspace(-xmax,xmax,num=100),
        np.linspace(-xmax,xmax,num=100))
    R = X**2 + Y**2
    Z = np.sqrt(1-X**2 - Y**2)
    Z[np.isnan(Z)] = 0
    THETA,PHI = hp.vec2ang(np.array([X,Y,Z]).T)
    THETA.shape = PHI.shape = X.shape
    PHI += rotate_angle*np.pi/180
    IM = get_interp_val(M,THETA,PHI).T
    IM = np.ma.masked_where(R>1,IM)
    return THETA,PHI,IM
def grid_theta_phi_to_healpix(theta,phi,inbeam):
    """
    inputs:
        theta (angle down from pixel 0, deg)
        phi (CW longitude angle, deg)
        inbeam: input beam values matching the corresponding theta and phi coords
    """
    print len(theta),len(phi),len(inbeam)
    nside = hp.npix2nside(len(inbeam))
    pixes = hp.ang2pix(nside,theta,phi)
    beam = np.zeros(hp.nside2npix(nside))
    rms = np.zeros(hp.nside2npix(nside))
    counts = np.zeros(hp.nside2npix(nside))
    for i,pix in enumerate(pixes):
        beam[pix] += inbeam[i]
        rms[pix] += inbeam[i]**2
        counts[pix] += 1
    beam[counts>0] /= counts[counts>0]
    rms[counts>0] /= counts[counts>0]
    rms -= beam**2
    rms = np.sqrt(rms)
    beam[counts==0] = hp.UNSEEN
    counts[counts==0] = hp.UNSEEN
    rms[counts==0] = hp.UNSEEN
    return beam,rms,counts
def grid_to_healpix(lats,lons,alts,rx,lat0,lon0,nside=8):
    """
    input:
        lats (deg)
        lons (deg)
        alts (m) (relative)
        rx: power in dB
        lat0: lat of rx ant (deg)
        lon0: lon of rx ant
        nside: of healpix map
    """
    # Convert lat/lon to x/y
    x,y = latlon2xy(lats,lons,lat0,lon0)
    # Obtain spherical coordinates for x, y, and alt
    rs,thetas,phis = to_spherical(x,y,alts)
    pixes = hp.ang2pix(nside,thetas,phis)
    beam = np.zeros(hp.nside2npix(nside))
    rms = np.zeros(hp.nside2npix(nside))
    counts = np.zeros(hp.nside2npix(nside))
    for i,pix in enumerate(pixes):
        beam[pix] += rx[i]
        rms[pix] += rx[i]**2
        counts[pix] += 1
    beam[counts>0] /= counts[counts>0]
    rms[counts>0] /= counts[counts>0]
    rms -= beam**2
    rms = np.sqrt(rms)
    beam[counts==0] = hp.UNSEEN
    counts[counts==0] = hp.UNSEEN
    rms[counts==0] = hp.UNSEEN
    #the standard deviation is uncertain for small counts
    #the the error in the standard deviation goes as 1/sqrt(2(N-1))
    #lets inflate the reported error to report the worst case upper limit
    #print 'Inflating error bars for low number counts'
    rms *= (1+1./np.sqrt(2*(counts-1)))
    return beam,rms,counts
def downgrade_rms(Map):
    #input a healpix map
    #return the standard deviation we'd get if we degraded to nside/2
    Map_nest = hp.reorder(Map,r2n=True)
    Map_nest = np.reshape(Map_nest,(len(Map)/4,4))
    return np.std(Map_nest,axis=1)
def make_beam(lats,lons,alts,spec_raw,lat0=0.0,lon0=0.0,
              nsides=8,volts=False,normalize=False,freq_chan=0):
    # Convert lat/lon to x/y
    x,y = latlon2xy(lats,lons,lat0,lon0)
    # Obtain spherical coordinates for x, y, and alt
    rs,thetas,phis = to_spherical(x,y,alts)

    #freq_chan = np.argmax(spec_raw[0,:])
    # Only extract information from appropriate column (index = 10)
    if len(spec_raw.shape)>1:
        z = spec_raw[:,freq_chan].copy()
    else:
        z=spec_raw.copy()
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
    hpx_beam[hpx_beam == 0] = np.nan
    hpx_counts[hpx_counts == 0] = np.nan
    hpx_rms[hpx_rms == 0] = np.nan

    return np.ma.masked_invalid(hpx_beam),\
           np.ma.masked_invalid(hpx_counts),\
           np.ma.masked_invalid(hpx_rms)


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


def animate_spectrum(i,spec_plot,spec_line,spec_raw):
    spec_line.set_ydata(spec_raw[i,:])
    #spec_plot.set_ylim([spec_raw[i,:].min(),spec_raw[i,:].max()])
    return


def animate_peak(i,peak_plot,peak_line,noise_line,pkrms_plot,pkrms_line,spec_times,\
                           spec_raw,peaktimes,peakvals,peakfreqs,rmss,peakrmss,freqs,\
                           fmin,fmax,time_range=200,rmswindow=10,freq=137.5):
    currtime = spec_times[i]
    if currtime == peaktimes[-1]:
        return peak_line,
    #peakfreq,peakval,rms = find_peak(freqs,spec_raw[i,:],fmin=fmin,fmax=fmax)
    freq_chan = np.where(np.abs(freqs-freq).min()==np.abs(freqs-freq))[0]
    peakfreq = freqs[freq_chan][0]
    peakval = spec_raw[i,freq_chan][0]
    rms = np.mean(spec_raw[i,freq_chan+10:freq_chan+50])
    peaktimes.append(currtime)
    peakvals.append(peakval)
    peakfreqs.append(peakfreq)
    rmss.append(rms)
    print peaktimes[-1],peakfreqs[-1],peakvals[-1],rmss[-1]

    labels = []
    for label in peak_plot.get_xticks():
        labels.append(gps_to_HMS(label,fmt='gps').split('.')[0])

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
    peak_plot.set_xticklabels(labels)
    noise_line.set_xdata(peaktimes)
    noise_line.set_ydata(rmss)

    # Update peak RMS plot
    pkrms_line.set_xdata(peaktimes)
    pkrms_line.set_ydata(peakrmss)
    pkrms_plot.relim()
    pkrms_plot.set_xlim([currtime-time_range,currtime])
    pkrms_plot.set_xticklabels(labels)
    pkrms_plot.autoscale_view(True,True,True)


def make_polycoll(hpx_beam,plot_lim=[-90,-50],nsides=8,cmap=cm.gnuplot):
    #pixnums = np.arange(len(hpx_beam))
    #theta,phi = hp.pix2ang(nsides,pixnums)
    #pix = pixnums[np.argwhere(theta<np.pi/2)].squeeze()
    pix = np.where(np.isnan(hpx_beam)==False)[0]
    boundaries = hp.boundaries(nsides,pix)
    verts = np.swapaxes(boundaries[:,0:2,:],1,2)
    coll = PolyCollection(verts, array=hpx_beam[np.isnan(hpx_beam)==False],\
                                    cmap=cmap,edgecolors='none')
    return coll


def animate_beam(beam_plot,hpx_beam,fig,cax,cbar,plot_lim=[-40,5],nsides=8):
    coll = make_polycoll(hpx_beam,nsides=8)#,plot_lim=plot_lim)
    cax.cla()
    cbar = fig.colorbar(coll, cax=cax, use_gridspec=True, label='dB')
    beam_plot.collections.remove(beam_plot.collections[-1])
    beam_plot.add_collection(coll)


def adjustErrbarxy(errobj, x, y, y_error):
    ln, (erry_top, erry_bot), barsy = errobj
    x_base = ln.get_xdata()
    y_base = y
    ln.set_ydata(y)
    yerr_top = y_base + y_error
    yerr_bot = y_base - y_error
    erry_top.set_xdata(x_base)
    erry_bot.set_xdata(x_base)
    erry_top.set_ydata(yerr_top)
    erry_bot.set_ydata(yerr_bot)
    new_segments_y = [np.array([[x, yt], [x,yb]]) for x, yt, yb in zip(x_base, yerr_top, yerr_bot)]
    barsy[0].set_segments(new_segments_y)


def animate_cuts(cuts_plot,cuts_E_line,cuts_H_line,hpx_beam,hpx_rms,ell,az):
    beam_slice_E = get_interp_val(hpx_beam,ell,az)
    beam_slice_E_err = get_interp_val(hpx_rms,ell,az)
    beam_slice_H = get_interp_val(hpx_beam,ell,az+np.pi/2)
    beam_slice_H_err = get_interp_val(hpx_rms,ell,az+np.pi/2)

    beam_slice_E = np.ma.masked_invalid(beam_slice_E)
    beam_slice_E_err = np.ma.masked_invalid(beam_slice_E_err)
    beam_slice_H = np.ma.masked_invalid(beam_slice_H)
    beam_slice_H_err = np.ma.masked_invalid(beam_slice_H_err)

    adjustErrbarxy(cuts_E_line,ell,beam_slice_E,beam_slice_E_err)
    adjustErrbarxy(cuts_H_line,ell,beam_slice_H,beam_slice_H_err)

    #cuts_plot.autoscale(axis='y')
    E_min = np.nanmin(beam_slice_E)-np.nanmin(beam_slice_E_err)
    H_min = np.nanmin(beam_slice_H)-np.nanmin(beam_slice_H_err)
    E_max = np.nanmax(beam_slice_E)+np.nanmax(beam_slice_E_err)
    H_max = np.nanmax(beam_slice_H)+np.nanmax(beam_slice_H_err)

    if not np.logical_and(np.isnan(E_min),np.isnan(H_min)):
        if not np.logical_and(np.isnan(E_max),np.isnan(H_max)):
            cuts_min = min(E_min,H_min)
            cuts_max = max(E_max,H_max)
            """
            print '----------------------'
            print E_min,H_min
            print E_max,H_max
            print cuts_min,cuts_max
            print '----------------------\n'
            """
            cuts_plot.set_ylim([cuts_min,cuts_max])

def add_cut_glyph(parent_fig=None,parent_axes=None,pos=(0.8,0.8),size=(.1),cut='NS',pol='NS'):
    #transformation stuff to put the little axis in the desired subplot
    if parent_fig is None:
        parent_fig = plt.gcf()
    if parent_axes is None:
        parent_axes = plt.gca()
    axtrans = parent_axes.transAxes
    figtrans = parent_fig.transFigure.inverted()
    figpos = figtrans.transform(axtrans.transform(pos)) #get the desired position in figure units
    pos = tuple(figpos)+ (size,size) #form up the extent box tuple
    ax = parent_fig.add_axes(pos,'square')
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_frame_on(False)
    myglyph = '/home/echo/src/ECHO/data/cut_glyphs_cut{cut}_rx{pol}_tx{pol}.png'.format(cut=cut,pol=pol)
    glyph = read_png(myglyph)
    ax.imshow(glyph,interpolation='none')
    return

def get_interp_val(m,theta,phi,nest=False):
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
    val = np.ma.sum(m2[p]*w/np.ma.sum(w,axis=0),axis=0)
    return val


def add_diagram(axs,xys,xytexts,colors,labels=None):
    for i in range(len(xys)):
        ax = axs[i]
        xy = xys[i]
        xytext = xytexts[i]
        color = colors[i]
        ax.annotate("",
                    xy=xy,
                    xycoords='axes fraction',
                    xytext=xytext,
                    textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='-',
                                    color=color,
                                    shrinkA=5, shrinkB=5,
                                    patchA=None,
                                    patchB=None,
                                    connectionstyle="arc3,rad=0.",
                                    ),
                    size=20)
        if not labels is None:
            label = labels[i]
            xyl = xy[:]
            if i == 0:
                xyl[0] += 0.05
            elif i == 1:
                xyl[1] += 0.05
            elif i == 2:
                xyl = (xy[0]+0.2,
                      xyl[1]+0.05)
            ax.annotate(label,
                        xy=xyl,
                        xycoords='axes fraction',
                        xytext=xyl,
                        textcoords='axes fraction',
                        arrowprops=dict(arrowstyle="-",
                                        color=color,
                                        shrinkA=5, shrinkB=5,
                                        patchA=None,
                                        patchB=None,
                                        connectionstyle="arc3,rad=0.",
                                        alpha=0.0
                                        ),
                        size=16)
