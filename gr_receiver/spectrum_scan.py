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

def zmq_consumer(socket_str):
    #input: URL and port (ex: tcp://127.0.0.1:5555
    #get data, make an array and do something with it
    context = zmq.Context()
    results_receiver = context.socket(zmq.PULL)
    results_receiver.connect(socket_str)
    raw_data = results_receiver.recv()
    data = np.frombuffer(raw_data,dtype=np.complex64)
    print(data.size/1024.) #i'm expecting 1024 complex numbers

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
B = 2e9
# and we knew that we had 
SDR_BW = 160e6 #UBX160 is what we have in Andri's X300s
#you can find out by running uhd_usrp_probe
nchunk = np.ceil(B/SDR_BW)
df = 100e3 #desired spectral resolution 100kHz would be reasonable for HERA
FFT_size = np.ceil(SDR_BW/df)
print("Scan Bandwidth [MHz]= ",B/1.e6)
print("SDR Bandwidth [kHz] =" ,SDR_BW/1.e3)
print("Number of chunks = ",nchunk)
print("FFT_size = ",FFT_size)
tunings = np.arange(nchunk)*SDR_BW + SDR_BW/2.

from spectrum import spectrum

def main(top_block_cls=spectrum,options=None):
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    socket_str = tb.get_data_address() #data are streaming from this ZMQ PUSH Sink
    for freq in tunings:#get chunks at each spectrum
        print("="*100)
	tb.set_tuning(freq)
        tb.start() 
        zmq_consumer(socket_str)
	#time.sleep(0.01)
        tb.stop()
        tb.wait()

if __name__ == '__main__':
    main()
