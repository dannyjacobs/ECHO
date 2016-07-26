import sys,optparse
import numpy as np
import healpy as hp
import matplotlib.gridspec as gridspec
from matplotlib.pyplot import *
from ECHO_plot_utils import make_polycoll,get_interp_val
from mpl_toolkits.axes_grid1 import make_axes_locatable
from operator import and_

o = optparse.OptionParser()
o.set_description('Queries ground station server for interpolated GPS position')

o.add_option('--base_beam',type=str,
    help='Base FITS file beam')
o.add_option('--adjusted_beam',type=str,
    help='FITS file for beam to be adjusted by --dB_shift')
o.add_option('--dB_shift',type=float,
    help='Amount to add/subtract to/from --mobile_beam in dB')
o.add_option('--nsides',type=int,default=8,
    help='Number of sides for Healpix plotting (Default = 8)')
o.add_option('--output_healpix',action='store_true',
    help='Output the beam healpix maps.')
opts,args = o.parse_args(sys.argv[1:])

badval = 1e20

ell = np.linspace(-np.pi/2,np.pi/2)
az = np.zeros_like(ell)
xticks = [-90,-60,-40,-20,0,20,40,60,90]

# Setup figure
fig = figure(figsize=(18,10))
gs = gridspec.GridSpec(2,4)


# Setup base_beam(rms)
base_beam = hp.read_map(opts.base_beam)
#base_beam = np.ma.masked_greater(base_beam,10)
base_beam = hp.ma(base_beam,badval=badval)
base_rms = hp.read_map(opts.base_beam.replace('beam','rms'))
base_rms = hp.ma(base_rms,badval=badval)
base_slice_H = get_interp_val(base_beam,ell,az)
base_slice_H_err = get_interp_val(base_rms,ell,az)
base_slice_E = get_interp_val(base_beam,ell,az+np.pi/2)
base_slice_E_err = get_interp_val(base_rms,ell,az+np.pi/2)
base_coll = make_polycoll(base_beam,nsides=opts.nsides)


# Setup adj_beam(rms)
adj_beam = hp.read_map(opts.adjusted_beam)
adj_beam = hp.ma(adj_beam,badval=badval)
adj_rms = hp.read_map(opts.adjusted_beam.replace('beam','rms'))
adj_rms = hp.ma(adj_rms,badval=badval)
adj_slice_H = get_interp_val(adj_beam,ell,az)
adj_slice_H_err = get_interp_val(adj_rms,ell,az)
adj_slice_E = get_interp_val(adj_beam,ell,az+np.pi/2)
adj_slice_E_err = get_interp_val(adj_rms,ell,az+np.pi/2)
adj_coll = make_polycoll(adj_beam,nsides=opts.nsides)


# Adjust adj_beam
shifted_beam = np.ma.array(adj_beam + opts.dB_shift)
shifted_rms = np.ma.array(adj_rms)
shifted_slice_H = get_interp_val(shifted_beam,ell,az)
shifted_slice_H_err = get_interp_val(shifted_rms,ell,az)
shifted_slice_E = get_interp_val(shifted_beam,ell,az+np.pi/2)
shifted_slice_E_err = get_interp_val(shifted_rms,ell,az+np.pi/2)
shifted_coll = make_polycoll(shifted_beam)


# Combine base_beam and adj_beam
combined_beam = np.ma.array(base_beam.filled(0)+shifted_beam.filled(0),
                            mask=(base_beam.mask*shifted_beam.mask))
combined_rms = np.ma.array(base_rms.filled(0)+shifted_rms.filled(0),
                            mask=(base_rms.mask*shifted_rms.mask))
# Create weights array for averaging beam overlap
base_mask = 1 - base_beam.mask.astype(int)
shifted_mask = 1 - shifted_beam.mask.astype(int)
weights = base_mask + shifted_mask
weights_inds = np.where(weights >= 1)[0]
combined_beam[weights_inds] /= 1.0*weights[weights_inds]
combined_rms[weights_inds] /= 1.0*weights[weights_inds]
combined_slice_H = get_interp_val(combined_beam,ell,az)
combined_slice_H_err = get_interp_val(combined_rms,ell,az)
combined_slice_E = get_interp_val(combined_beam,ell,az+np.pi/2)
combined_slice_E_err = get_interp_val(combined_rms,ell,az+np.pi/2)
combined_coll = make_polycoll(combined_beam,nsides=opts.nsides)

if opts.output_healpix:
    hp.write_map(str(opts.nsides)+'_combined_beam.fits',combined_beam)
    hp.write_map(str(opts.nsides)+'_combined_rms.fits',combined_rms)




################# Beam Plotting #################

# Plot base_beam as PolyCollection
base_beam_plot = fig.add_subplot(gs[0,0],aspect='equal')
base_beam_plot.add_collection(base_coll)
base_beam_plot.autoscale_view()
base_beam_plot.set_title('Base')

# Plot adj_beam as PolyCollection
adj_beam_plot = fig.add_subplot(gs[0,1],aspect='equal')
adj_beam_plot.add_collection(adj_coll)
adj_beam_plot.autoscale_view()
adj_beam_plot.set_title('Adjusted')

# Plot shifted_beam as PolyCollection
shift_beam_plot = fig.add_subplot(gs[2],aspect='equal')
shift_beam_plot.add_collection(shifted_coll)
shift_beam_plot.autoscale_view()
shift_beam_plot.set_title('Adjusted + (%f) dB' %(opts.dB_shift))

# Plot combined_beam as PolyCollection
comb_beam_plot = fig.add_subplot(gs[3],aspect='equal')
comb_beam_plot.add_collection(combined_coll)
comb_beam_plot.autoscale_view()
comb_beam_plot.set_title('Combined')



################# Cuts Plotting #################

# Plot base_beam cuts
base_cuts_plot = fig.add_subplot(gs[1,0])
base_cuts_plot.errorbar(ell*180/np.pi,
                        base_slice_E,
                        base_slice_E_err,
                        fmt='b.',
                        label='E')
base_cuts_plot.errorbar(ell*180/np.pi,
                        base_slice_H,
                        base_slice_H_err,
                        fmt='r.',
                        label='H')

# Plot adj_beam cuts
adj_cuts_plot = fig.add_subplot(gs[1,1])
adj_cuts_plot.errorbar(ell*180/np.pi,
                       adj_slice_E,
                       adj_slice_E_err,
                       fmt='b.',
                       label='E')
adj_cuts_plot.errorbar(ell*180/np.pi,
                       adj_slice_H,
                       adj_slice_H_err,
                       fmt='r.',
                       label='H')

# Plot shifted_beam cuts
shifted_cuts_plot = fig.add_subplot(gs[1,2])
shifted_cuts_plot.errorbar(ell*180/np.pi,
                           shifted_slice_E,
                           shifted_slice_E_err,
                           fmt='b.',
                           label='E')
shifted_cuts_plot.errorbar(ell*180/np.pi,
                           shifted_slice_H,
                           shifted_slice_H_err,
                           fmt='r.',
                           label='H')

# Plot combined_beam cuts
combined_cuts_plot = fig.add_subplot(gs[1,3])
combined_cuts_plot.errorbar(ell*180/np.pi,
                            combined_slice_E,
                            combined_slice_E_err,
                            fmt='b.',
                            label='E')
combined_cuts_plot.errorbar(ell*180/np.pi,
                            combined_slice_H,
                            combined_slice_H_err,
                            fmt='r.',
                            label='H')

for i,ax in enumerate(fig.axes):
    if i < 4:
        ax.set_xlim([-1,1])
        ax.set_ylim([-1,1])
        # Position colorbar next to plot with same height as plot
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = fig.colorbar(ax.collections[0],
                            cax=cax,
                            use_gridspec=True,
                            label='dB',
                            format='%d')
    elif i >= 4:
        ax.set_ylabel('dB')
        ax.set_xlabel('Elevation Angle [deg]')
        ax.legend(loc='lower center',ncol=2)
        ax.set_ylim([-90,-40])


fig.tight_layout()

show()
