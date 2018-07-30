#! /usr/bin/env python

import numpy as n,os,sys
import healpy as hp
import sys,optparse
from pylab import *
from scipy import optimize
from ECHO.plot_utils import get_interp_val,add_cut_glyph
from ECHO.read_utils import read_map
style.use(os.path.dirname(__file__)+'/echo.mplstyle')
o = optparse.OptionParser()
o.set_description('plot slices of GB healpix maps')
o.add_option('--savefig',type=str,help='output figure name')
o.add_option('--exp',action='store_true',help='do experimental stuff')
opts,args = o.parse_args(sys.argv[1:])

base_model = '/home/echo/Downloads/BicoLOG_results_ff137.fits'
vader_model = '/home/echo/Downloads/Vader_results_ff137.fits'


#Try a short dipole model.

#cross cut coordinates
print "plotting E and H plane slices"
alt = n.linspace(-n.pi/2,n.pi/2)
az = n.zeros_like(alt)

#get the base bicolog model
base_map = read_map(base_model)
base_map -= np.mean(base_map[:3])
base_slice_E = get_interp_val(base_map,alt,az)
base_slice_H = get_interp_val(base_map,alt,az+np.pi/2)

#get the vader model
vader_map = read_map(vader_model)
vader_map -= np.mean(base_map[:3])
vader_slice_E = get_interp_val(vader_map,alt,az)
vader_slice_H = get_interp_val(vader_map,alt,az+np.pi/2)

#altfig = figure(figsize=(8,6))
fig,axarr = subplots(2,3,figsize=(15,6),sharey=False,sharex=True)

E_color = 'k'
H_color = 'k'
ls = ['s','d','d','s'] #file order is north, south, south, north

#plot the base model
axarr[0,0].plot(alt*180/np.pi,base_slice_E,'-k',lw=2)
axarr[0,1].plot(alt*180/np.pi,vader_slice_E,'-k',lw=2)
axarr[0,2].plot(alt*180/np.pi,base_slice_E-vader_slice_E,'-k',lw=2)
axarr[1,0].plot(alt*180/np.pi,base_slice_H,'-k',lw=2)
axarr[1,1].plot(alt*180/np.pi,vader_slice_H,'-k',lw=2)
axarr[1,2].plot(alt*180/np.pi,base_slice_H-vader_slice_H,'-k',lw=2)
#legend(loc='best')
axarr[0,0].set_title('Base')
axarr[0,1].set_title('Vader')
axarr[0,2].set_title('Base - Vader')
axarr[0,0].set_ylabel('E plane\n [dB V/m]')
axarr[1,0].set_ylabel('H plane\n [dB V/m]')
axarr[1,0].set_xlabel('$\\theta$ (deg)')
axarr[1,1].set_xlabel('$\\theta$ (deg)')
axarr[1,2].set_xlabel('$\\theta$ (deg)')
#axes
subplots_adjust(hspace=.1,wspace=.2)
axarr[0,0].set_ylim(-20,2)
axarr[0,1].set_ylim(-20,2)
axarr[0,2].set_ylim(-3,3)
axarr[1,0].set_ylim(-10,2)
axarr[1,1].set_ylim(-10,2)
axarr[1,2].set_ylim(-3,3)
for ax in axarr.ravel():
    ax.grid(which='both') #turn on everyones grid
    ax.xaxis.set_ticks(np.arange(-80,100,20))

if not opts.savefig is None:
    print "plotting to", opts.savefig
    fig.savefig(opts.savefig)
else:
	show()
