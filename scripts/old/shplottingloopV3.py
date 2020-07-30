#! /usr/bin/env python
from matplotlib import use
use('TkAgg')
import numpy as n
import matplotlib.pyplot as plt
import datetime as date
from pylab import *
import sys
import matplotlib.animation as animation

rmswindow=10 #number of samples over which to compute the rms of the peak
filename = sys.argv[1]
if len(open(filename).readlines())<3:
    print "error, file too short. Exiting"
    sys.exit()
#fmin = 914.5 #MHz
#fmax = 915.5 #MHz
fmin = 136
fmax = 138
time_range = 200 #time range in seconds of peak plot

def select_data_by_frequency(f,x,fmin=0,fmax=500,freq=137.5):
    freq_chan = np.where(np.abs(f-freq).min()==np.abs(f-freq))[0]
    peak = x[freq_chan]
    maxfreq = f[freq_chan]
    peakrms = np.mean(x[freq_chan+10:freq_chan+50])
    return maxfreq,peak,peakrms

def find_peak(f,x,fmin=0,fmax=500,freq=137.5):
    # f = frequencies in MHz
    # x = spectrum
    # fmin,fmax range in which to search for peak
    fchans = np.argwhere(np.logical_and(f>fmin,f<fmax))

    #peak = x[fchans].max()
    peak = x[freq_chan]
    #maxfreq = f[fchans[x[fchans].argmax()]]
    maxfreq = f[freq_chan]
    peakrms = np.mean(x[fchans.max():fchans.max()+100])
    return maxfreq,peak,peakrms

def get_SHdata():
    lines = open(filename).readlines()
    freqs = map(float,lines[1].split(','))
    ncol = len(freqs)
    D = [freqs]
    for line in lines[1:]:
        if line.startswith('#'):continue
        if len(line.split(',')) == ncol:
            D.append(map(float,line.split(',')))
    D = n.array(D)
    return D


#initialize the spectrum plot
figure1 = plt.figure(num= None, figsize=(10,6), dpi=80, facecolor='w', edgecolor='w')
ax1 = figure1.add_subplot(111)
D = get_SHdata()
print "found file:",filename
print "found frequencies in range:",D[0,1],D[0,-1]

line1, = ax1.plot(D[0,1:],D[-1,1:])
plt.vlines([fmin,fmax],ymin=-100,ymax=10)
#plt.show(block = False)
plt.xlabel("Frequency [Mhz]")
plt.ylabel("Power [dBm]")


#initialize the peak plot
last_time = D[-1,0] #t
figure2 = plt.figure(figsize=(10,6),facecolor='w',edgecolor='w')
ax2 = figure2.add_subplot(211)
ax2.autoscale_view(True,True,True)
peakfreq,peakval,rms = select_data_by_frequency(D[0,1:],D[-1,1:],fmin=fmin,fmax=fmax)
peaktimes = [D[-1,0]]
peakvals = [peakval]
peakfreqs = [peakfreq]
rmss = [rms]
peakrmss = [0]
line2, = ax2.plot(peaktimes,peakvals,label='peak')
ylabel('peak power [dBm]')
#ax3 = twinx()
line3, = ax2.plot(peaktimes,rmss,'k',label='noise')
ax2.legend(loc='upper left')
plt.show(block=False)
plt.xlabel('time [s]')
plt.ylabel('rms error [dBm]')
ax3 = figure2.add_subplot(212)
line4,=ax3.plot(peaktimes,peakrmss,'k',label='peak_variability')
plt.xlabel('time [s]')
plt.ylabel('peak rms [dB]')
ax3.legend(loc='upper left')
def animate_spectrum(i):
    try:
        D = get_SHdata()
        line1.set_ydata(D[-1,1:])
        #find peak within fmin,fmax
        #write time, peak value, freq to file
        # update peak vs time plot
        return line1,
    except(KeyboardInterrupt):
        sys.exit()
def init_spectrum():
    line1.set_ydata(n.zeros_like(D[-1,1:]))
    return line1,

def animate_peak(i):
    try:
        D = get_SHdata()
        time = D[-1,0]
        if time==peaktimes[-1]:return line2,
        frequencies = D[0,1:]
        spectrum = D[-1,1:]
        peakfreq,peakval,rms = select_data_by_frequency(frequencies,spectrum,fmin=fmin,fmax=fmax)
        peaktimes.append(time)
        peakvals.append(peakval)
        peakfreqs.append(peakfreq)
	rmss.append(rms)
	if len(peakvals)<rmswindow:
	    peakrmss.append(n.std(peakvals))
        else:
            peakrmss.append(n.std(peakvals[-rmswindow:]))
        print peaktimes[-1],peakfreqs[-1],peakvals[-1],n.round(rmss[-1],3),n.round(peakrmss[-1],2)
        line2.set_ydata(peakvals)
        line2.set_xdata(peaktimes)
        line3.set_ydata(rmss)
	line3.set_xdata(peaktimes)
	line4.set_ydata(peakrmss)
	line4.set_xdata(peaktimes)
        ax2.relim()
        ax2.autoscale_view(True,True,True)
        ax2.set_xlim([time-time_range,time])
        ax3.relim()
	ax3.set_xlim([time-time_range,time])
        ax3.autoscale_view(True,True,True)

        #ax3.autoscale_view(True,True,True)
        return line2,
    except(KeyboardInterrupt):
        sys.exit()

def init_peak():
    line2.set_ydata(peakvals)
    line2.set_xdata(peaktimes)
    return line2,
#ani = animation.FuncAnimation(figure1, animate_spectrum,init_func=init_spectrum, interval=25)#, blit=True)
ani2 = animation.FuncAnimation(figure2, animate_peak,init_func=init_peak, interval=25)

show()
