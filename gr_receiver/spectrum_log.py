# Python script which scans the spectrum
from __future__ import print_function
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from spectrum import spectrum,zmq_min_max_avg
from astropy.time import Time


def round_to_nearest_2(x):
    return 2**(x-1).bit_length()


def dB(x):
    return 10*np.log10(x)

#TUNABLE PARAMETERS
#record a waterfall at a given freq
freq = 120e6
sample_interval = .1
df = 200e3 #desired spectral resolution 100kHz would be reasonable for HERA
plot_int = 1 #plot every plot_int spectra
exp_name = 'hera' #add this name to the filename string to help identify it

##SDR parameters
SDR_BW =160e6

FFT_size = int(np.ceil(SDR_BW/df))
FFT_size = round_to_nearest_2(FFT_size)
nreads = 1000
print("FFT_size = ",FFT_size)
 #time between spectra in seconds
#freqs = np.linspace(0,np.ceil(SDR_BW/df),num=FFT_size)*df+freq/2
freqs = (np.arange(FFT_size)-FFT_size/2)*df + freq
print("freq range = ",freqs.min()/1e6,freqs.max()/1e6)


t = Time.now()
d = t.isot.replace(':','_')
filename = "ECHO_{n}_{d}.txt".format(n=exp_name,d=d)

#start a data file
f = open(filename,'w>')
f.write("# ECHO Spectrum data file\n")
f.write("# Start Date: {d}\n".format(d=d))
f.write('# freqs: {freqs}\n'.format(freqs=','.join(freqs.astype(str))))
f.write("# data type, time (julian date), power in dB\n")
print("logging to:{filename}".format(filename=filename))


fig = plt.figure()
def main(top_block_cls=spectrum,options=None):
    tb = top_block_cls(FFT_size,SDR_BW)
    socket_str = tb.get_data_address() #data are streaming from this ZMQ PUSH Sink
    tb.set_tuning(freq)
    tb.start()
    i=0
    while True:
        try:
            #time.sleep(0.5)
            t = Time.now()
            min_accum,max_accum,mean_accum = zmq_min_max_avg(socket_str,FFT_size,nreads=nreads) #data should be NchanxNtimes long where Ntimes floats around but is generally 2-6  
            #write out data
            f.write("MEAN, "+ str(t.jd)+', ')
            f.write(','.join(dB(mean_accum).astype(str)))
            f.write('\n')
            print('.',end='')
            
            #Plotting
            if i%plot_int == 0:
                plt.clf()
                plt.plot(freqs/1e6,dB(mean_accum),'k',label='mean')
                plt.plot(freqs/1e6,dB(max_accum),':k',label="max")
                plt.grid()
                plt.legend()
                plt.xlabel('freq [MHz]')
                plt.ylabel('dB')
                plt.title('ECHO spectrometer')
                plt.vlines(137.5,dB(mean_accum.min()),dB(mean_accum.max()))
                plt.pause(sample_interval)
            time.sleep(sample_interval)
            i += 1
            sys.stdout.flush()
        except(KeyboardInterrupt):
            sys.exit()
#        tb.stop()
#        tb.wait()

if __name__ == '__main__':
    main()
