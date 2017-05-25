#!/usr/bin/env python

from astropy.io import fits
import healpy as hp
from pylab import *

d=fits.open(sys.argv[1])
dmap=d['BEAM_E'].data
hp.mollview(dmap[:,0])

s=fits.open(sys.argv[2])
smap=s['BEAM_E'].data
hp.mollview(smap[:,0])

cmap=s['BEAM_E'].data - d['BEAM_E'].data
hp.mollview(cmap[:,0])

show()
