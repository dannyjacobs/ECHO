# Python script which builds a bandpass model
# RUN WITH 50ohm termination 

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

def dB(x):
    return 10*np.log10(x)
def zmq_consumer(socket_str,FFT_size,nreads=1):
    #input: URL and port (ex: "tcp://127.0.0.1:5555")
    #       nreads number of times to read from the socket
    #get data, make an array and do something with it
    context = zmq.Context()
    results_receiver = context.socket(zmq.PULL)
    results_receiver.connect(socket_str)
    data_stack = []
    for i in xrange(nreads):
        data_buffer = results_receiver.recv()
        data = np.frombuffer(data_buffer,dtype=np.complex64)
        data.shape = (data.size/FFT_size,FFT_size)
        data_stack.append(data)
    return np.vstack(data_stack)

def zmq_min_max_avg(socket_str,FFT_size,nreads=1):
    #input: URL and port (ex: "tcp://127.0.0.1:5555")
    #       nreads number of times to read from the socket
    #get data, make an array and do something with it
    context = zmq.Context()
    results_receiver = context.socket(zmq.PULL)
    results_receiver.connect(socket_str)
    mean_accum = np.zeros(FFT_size)
    count_accum = np.zeros(FFT_size)
    max_accum = np.zeros(FFT_size)
    min_accum = np.zeros(FFT_size)
    for i in xrange(nreads):
        data_buffer = results_receiver.recv()
        data = np.frombuffer(data_buffer,dtype=np.complex64)
        data.shape = (data.size/FFT_size,FFT_size)
        data = np.abs(data)
        mean_accum += np.sum(data,axis=0)
        max_accum = np.max(np.vstack([max_accum,data]),axis=0)
        min_accum = np.min(np.vstack([min_accum,data]),axis=0)
        count_accum += data.shape[0]
    mean_accum = mean_accum[count_accum>0]/count_accum[count_accum>0]
    return min_accum,max_accum,mean_accum


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
# integrate to beat down noise
# save out the averaged thing


# suppose we wanted 2GHz of total bw
B = 2e9
df = 100e3 #desired spectral resolution 100kHz would be reasonable for HERA
inttime = 10 #integration time in s

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
n_integration = int(np.ceil(df*inttime)/1e3) #/1e3 for cpu duty cycle??

tunings = np.arange(nchunk)*SDR_BW + SDR_BW/2.
nchan = nchunk*FFT_size
print("total number of channels in spectrum = ",nchan)
print("summing up n_integrations:",n_integration)
data = np.zeros(shape=(3,nchunk,FFT_size))

def main(top_block_cls=spectrum,options=None):
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(FFT_size,SDR_BW)
    socket_str = tb.get_data_address() #data are streaming from this ZMQ PUSH Sink
    for i,freq in enumerate(tunings):#get chunks at each spectrum
        print(i,freq)
	tb.set_tuning(freq)
        tb.start() 
        min_spectrum,max_spectrum,avg_spectrum = zmq_min_max_avg(socket_str,FFT_size=FFT_size,nreads=n_integration) #get average data
        data[:,i] = [min_spectrum,max_spectrum,avg_spectrum]
        tb.stop()
        tb.wait()

    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors=prop_cycle.by_key()['color']

    freqs = np.linspace(0,np.ceil(B/df),num=len(data))*df
    chans = np.arange(FFT_size)
    for i,freq in enumerate(tunings):
	color=colors[i%len(colors)]
    	#plt.fill_between(chans,data[0,i],y2=data[1,i])
	plt.plot(chans,dB(data[1,i]),color=color,label=str(freq/1e6))
        plt.plot(chans,dB(data[2,i]),color=color)
        
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
