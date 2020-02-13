#! /usr/bin/env python
from ECHO.read_utils import read_apm_log,apm_version,read_echo_spectrum
import sys
from pytz import timezone
TZ = 'US/Arizona'
tz = timezone(TZ)


for filename in sys.argv[1:]:
    print filename

    apm_times,freqs,data =read_echo_spectrum([filename])
    print "GPS start (UTC):",apm_times[0].iso
    print "GPS end (UTC):",apm_times[-1].iso

    print "GPS start ({z}):".format(z=TZ),apm_times[0].to_datetime(timezone=tz)
    print "GPS end ({z}):".format(z=TZ),apm_times[-1].to_datetime(timezone=tz)

    print "freqs (min,max) [MHz]:",freqs.min(),freqs.max()
