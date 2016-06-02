import numpy as np
import sys
from astropy.time import Time

times = np.loadtxt(sys.argv[1],delimiter=',',skiprows=1,usecols=[0])
times = Time(times,format='unix',scale='utc')
print 'File:\t' + sys.argv[1]
print 'Start time:\t' + times[0].iso
print 'Stop time:\t' + times[-1].iso + '\n'
