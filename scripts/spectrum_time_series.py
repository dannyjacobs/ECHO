import numpy as np
import optparse

from matplotlib.pyplot import *

o = optparse.OptionParser()
o.set_description('Queries ground station server for interpolated GPS position')
o.add_option('--spec_file',type=str,help='Accumulated file for plotting')
o.add_option('--freq',type=float,default=137.5,help='Peak frequency to look for in data')
o.add_option('--width',type=int,default=500,help='Number of channels to include in spectrum analysis')
opts,args = o.parse_args(sys.argv[1:])


spec = np.genfromtxt(opts.spec_file,skip_header=1,skip_footer=1,delimiter=',')
freqs = spec[0,1:]
freq_chan = np.where(np.abs(freqs-opts.freq).min()==np.abs(freqs-opts.freq))[0]
spec_raw = spec[1:,1:]
spec_times = spec[1:,0]
spec_times -= spec_times.min()
print '\nRead in %d spectra spanning %d frequencies...' %(spec_raw.shape[0],freqs.shape[0])

figure(figsize=(10,10))
title(opts.spec_file + ', Plotting frequency: ' + str(opts.freq) + ' MHz')
plot(spec_times,spec_raw[:,freq_chan],'k.')
xlim([spec_times.min(),spec_times.max()])
ylabel('dB')
xlabel('Unix Time [s]')
tight_layout()

'''
fig2 = figure(figsize=(3.75,12))
ax2 = fig2.add_subplot(111,aspect='auto')
ax2.imshow(spec_raw)
ylabel('Unix Time [s]')
xlabel('Frequency [MHz]')
tight_layout()
'''

show()


