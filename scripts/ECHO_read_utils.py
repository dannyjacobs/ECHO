import numpy as np


def get_data(infile,filetype=None,freqs=[],freq=0.0,freq_chan=None,ant=None,dip=None,width=100):
    if filetype == 'gps':
        gps_arr = []
        lines = open(infile).readlines()
        count = len(lines)
        gps_arr = [map(float,line.rstrip('\n').split(',')) for line in lines[2:] if len(line.split(','))==4 and not line.startswith('#')]
        return np.array(gps_arr)

    elif filetype == 'sh':
        spec_times = []
        spec_raw = []
        lines = open(infile).readlines()
        count = len(lines)
        if count != 0:
            if len(freqs) == 0:
                freqs = np.array(map(float,lines[1].rstrip('\n').split(',')[1:]))
                freq_chan = np.where(np.abs(freqs-freq).min()==np.abs(freqs-freq))[0] # Get index of freq for gridding            
		freqs = freqs[freq_chan-width:freq_chan+width] # freq is freqs[10]
            for line in lines[2:]:
                if line.startswith('#'):
                    continue
                line = line.rstrip('\n').split(',')
                if len(line) == 4097: # Make sure line has finished printing
                    spec_times.append(float(line[0]))
                    spec_raw.append(map(float,line[freq_chan-width:freq_chan+width]))
        return np.array(spec_times),np.array(spec_raw),np.array(freqs),freq_chan

    elif filetype == 'echo':
        all_Data = []
        freqs = []
        #print '\nReading in %s...' %inFile
        lines = open(infile).readlines()
        # Add information from flight to all_Data array
        lat0,lon0 = map(float,lines[2].rstrip('\n').split(':')[1].strip(' ').split(','))
        freqs = map(float,lines[3].rstrip('\n').split(':')[1].strip(' ').split(','))
        freqs = np.array(freqs)
        for line in lines[:]: # Data begins on fifth line of accumulated file
            if line.startswith('#'):
                continue
            elif not line.split(',')[1] == '-1':
                    all_Data.append(map(float,line.rstrip('\n').split(',')))
        all_Data = np.array(all_Data)
        #print 'Converted to array with shape %s and type %s' %(all_Data.shape,all_Data.dtype)
        spec_times,lats,lons,alts,spec_raw = (all_Data[:,0],all_Data[:,1],all_Data[:,2],\
                                                                        all_Data[:,3],all_Data[:,4:])
        return spec_times,spec_raw,freqs,lats,lons,alts,lat0,lon0

    elif filetype == 'orbcomm':
        all_Data = []
        lines = open(infile).readlines()
        for line in lines[:]: # Data begins on fifth line of accumulated file
            if line.startswith('#'):
                continue
            elif not line.split(',')[1] == '-1':
                    all_Data.append(map(float,line.rstrip('\n').split(',')))
        all_Data = np.array(all_Data)
        spec_times,lats,lons,alts,yaws = (all_Data[:,1],all_Data[:,2],all_Data[:,3],\
                                                        all_Data[:,4],all_Data[:,5])
        if ant == 'N':
            lat0,lon0 = (38.4248532,-79.8503723)
            if 'NS' in inFile:
                spec_raw = all_Data[:,12:17] # N antenna, NS dipole
            if 'EW' in inFile:
                spec_raw = all_Data[:,24:29] # N antenna, EW dipole
        elif ant == 'S':
            lat0,lon0 = (38.4239235,-79.8503418)
            if 'NS' in inFile:
                spec_raw = all_Data[:,6:11] # S antenna, NS dipole
            if 'EW' in inFile:
                spec_raw = all_Data[:,18:23] # S antenna, EW dipole
        return spec_times,lats,lons,alts,yaws,spec_raw

    else:
        print '\nNo valid filetype found for %s' %infile
        print 'Exiting...\n\n'
        sys.exit()
