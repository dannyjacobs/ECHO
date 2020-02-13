#! /usr/bin/env python

import valon_synth as vs
import sys
import optparse

o = optparse.OptionParser()
o.add_option('--freq',type=float, help='Frequency in MHz to be set for SYNTH_A')
o.add_option('--Bfreq',type=float, help='Frequency in MHZ to be set for SYNTH_B')
o.add_option('--rflevel',type=float,help='RF level in dB to be set for SYNTH_A')
o.add_option('--Brflevel',type=float,help='RF level in dB to be set for SYNTH_B')
o.add_option('-p',action="store_false",default=True,help='Command to print existing settings')
opts,args = o.parse_args()

# All functions from valon_synth return booleans for success/failure (true/false)

# Read in USB port number in format '/dev/ttyUSB#'
# '#' is port number found from issuing dmesg after pluggin in USB
# Device will be recorded as FTDI chip in dmesg | tail -1 (last line)
# FTDI device frequents to port 0 (may not always be the same)
loc = '/dev/ttyUSB0'

# Declare synthesizer object for communication
mySynth = vs.Synthesizer(loc)

# 0 = SYNTH_A, 8 = SYNTH_B
aFreq = mySynth.get_frequency(0)
bFreq = mySynth.get_frequency(8)
aRF = mySynth.get_rf_level(0)
bRF = mySynth.get_rf_level(8)

# If no options passed, print existing values
if not opts.p is True:
   print "\nSYNTH_A, SYNTH_B:"
   print "Frequency: %0.4f, %0.4f" %(aFreq,bFreq)
   print "RF Level: %d, %d\n" %(aRF,bRF)
# Modify values if
else:
   if not opts.freq is None:
      # Set new frequency for SYNTH_A
      mySynth.set_frequency(0,opts.freq)
      aFreq = mySynth.get_frequency(0)

   if not opts.rflevel is None:
      # Set new RF level for SYNTH_A
      mySynth.set_rf_level(0,opts.rflevel)
      aRF = mySynth.get_rf_level(0)

   if not opts.Bfreq is None:
      # Set new frequency for SYNTH_B
      mySynth.set_frequency(8,opts.Bfreq)
      bFreq = mySynth.get_frequency(8)

   if not opts.Brflevel is None:
      # Set new RF level for SYNTH_B
      mySynth.set_rf_level(8,opts.Brflevel)
      bRF = mySynth.get_rf_level(8)

   # Flash settings to memory
   success = mySynth.flash()

   if success:
      # Print info for A, B
      print "\nSYNTH_A, SYNTH_B:"
      print "Frequency: %0.2f, %0.2f" %(aFreq,bFreq)
      print "RF Level: %d, %d" %(aRF,bRF)
      print "\nSettings flashed successfully.\n"
   else:
      print "\nError flashing settings to memory. Exiting...\n"
      sys.exit()
