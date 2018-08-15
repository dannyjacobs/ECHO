# Python script which scans the spectrum

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
import sys
import time
import zmq
import numpy as np
import matplotlib.pyplot as plt


def round_to_nearest_2(x):
    return 2**(x-1).bit_length()


def zmq_consumer(socket_str):
    #input: URL and port (ex: "tcp://127.0.0.1:5555")
    #get data, make an array and do something with it
    context = zmq.Context()
    results_receiver = context.socket(zmq.PULL)
    results_receiver.connect(socket_str)
    raw_data = results_receiver.recv()
    data = np.frombuffer(raw_data,dtype=np.complex64)
    return np.array(data)

#given a range of frequencies and resolution
# divide the range into discrete chunks
# scan through the chunks 
# do a min/max/avg across time
#the input to getting a chunk is
# sample_rate - comes from center freq
# FFT_size - comes from spectral resolution
# integration number - number of FFTs to average before handing back
#           this last could be as little as 1, but in practice will depend on the noise level we want vs the scan rate.
#   Given the sample rate we can estimate the scan rate (integration_time * Nchunks)
#  where Nchunks is desired bandwidth/available sdr bandwidth
#  This means we need to know the true available bandwidth of the SDR

# suppose we wanted 2GHz of total bw
B = 2e9 #scan range in Hz
df = 100e3 #desired spectral resolution 100kHz would be reasonable for HERA
start_freq = 10e6 #start the scan at this freq
from spectrum import spectrum

#SDR parameters
SDR_BW = 160e6
# and we knew that we had 
#you can find out by running uhd_usrp_probe
nchunk = np.ceil(B/SDR_BW)
FFT_size = int(np.ceil(SDR_BW/df))
FFT_size = round_to_nearest_2(FFT_size)
print("Scan Bandwidth [MHz]= ",B/1.e6)
print("SDR Bandwidth [MHz] =" ,SDR_BW/1.e6)
print("Number of chunks = ",nchunk)
print("FFT_size = ",FFT_size)
tunings = np.arange(nchunk)*SDR_BW + SDR_BW/2. + start_freq
nchan = nchunk*FFT_size
print("total number of channels in spectrum = ",nchan)
data = np.zeros(nchan)

def main(top_block_cls=spectrum,options=None):
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(FFT_size,SDR_BW)
    socket_str = tb.get_data_address() #data are streaming from this ZMQ PUSH Sink
    for i,freq in enumerate(tunings):#get chunks at each spectrum
        print(i,freq)
	tb.set_tuning(freq)
        tb.start() 
        data_buffer = zmq_consumer(socket_str) #data should be NchanxNtimes long where Ntimes floats around but is generally 2-6
        Ntimes = data_buffer.size/FFT_size
        data_buffer.shape = (Ntimes,FFT_size) #its either this order or the other one
        data_buffer = np.abs(data_buffer) #power spectrum
        data_buffer_mean = np.mean(data_buffer,axis=0)
        data[i*FFT_size:(i+1)*FFT_size] = data_buffer_mean
        tb.stop()
        tb.wait()
    freqs = np.linspace(0,np.ceil(B/df),num=len(data))*df
    plt.plot(freqs/1e6,10*np.log10(data))
    #plt.plot(data)
    plt.show()

if __name__ == '__main__':
    main()
