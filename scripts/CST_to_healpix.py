#! /usr/bin/env python

import numpy as n,sys,os
import healpy as hpy
import optparse
from pylab import *

#
######################### Opts #############################

o = optparse.OptionParser()
o.set_description('Convert a CST output txt file into a healpix map')
o.add_option('--nside',type=int,default=8,help='nside of output map')
o.add_option('--rot90',action='store_true',help='rotate around the pole by 90 degrees')
o.add_option('--flup',action='store_true',help='invert the z axis. good for changing tx beam into the rx frame')
o.add_option('--voltage',action='store_true',help='convert from dB to linear voltage amplitude')
o.add_option('-o', '--outfile', dest='outfile', default='healpix_beam.fits', help='Output filename')
opts,args = o.parse_args(sys.argv[1:])

if opts.rot90:
    outfile = args[0].replace('.txt','_rot90.fits')
else:
    outfile = args[0].replace('.txt','.fits')
outfile = os.path.basename(outfile)
print("writing", outfile)
#load the input CST txt file
#find the healpix indices corresponding to the theta/phi
#make a healpix map


D = n.loadtxt(args[0],skiprows=3)
theta = D[:,0]*n.pi/180
#CST will output either elev or phi. phi is zero at beam x=y=0, elev is zero at x=0,phi=0
if open(args[0]).readlines()[0].startswith('Elev'): theta += n.pi/2
phi = D[:,1]*n.pi/180
#account for stupid CST full circle cuts
phi[theta<0] += np.pi
theta[theta<0] = np.abs(theta[theta<0])
beam = D[:,2] #beam amplitude in dB
if opts.rot90:
    phi += n.pi/2
if opts.flup:
    theta = np.pi - theta
healpix_indexes = hpy.ang2pix(opts.nside,theta,phi)

hp_map = n.zeros(hpy.nside2npix(opts.nside))

hp_map[healpix_indexes] = beam
hp_map -= hp_map[0]

if opts.voltage:
    hp_map = 10**(hp_map/20.)
print("max/min",hp_map.max(),hp_map.min())
hpy.write_map(outfile,hp_map,fits_IDL=False)
print("Write successfull")
