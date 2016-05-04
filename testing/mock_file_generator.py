import numpy as np
import sys

def Guassian(a,b,c,x,y):
    # a: amplitude
    # b: mean
    # c: std dev
    return a*np.exp(-((x-b)**2+(y-b)**2)/(2*c**2))

outFile = 'exemplary_output_file.txt'
with open(outFile,'wb') as f:
   print 'New file created: ',outFile

r_earth = 6.3781e6
freqs = [137.505,137.51,137.515,137.519,137.524,\
            137.529,137.534,137.539,137.544,137.549,\
            137.554,137.559,137.563,137.568,137.573,\
            137.578,137.583,137.588,137.593,137.598]
lat0,lon0 = 33.41865,-111.9295
t0 = 1145210544.0
line1 = '# Accumulated data for 20_04_2016, 11:02:55\n'
line2 = '# Column Format: 1 Time [GPS s], 2 Lat [deg], 3 Lon [deg], 4 Rel Alt [m], 5: Radio Spectrum\n'
line3 = '# lat0,lon0: '+str(lat0)+','+str(lon0)+'\n'
line4 = '# Freqs: '+','.join(map(str,freqs))+'\n'
with open(outFile,'ab') as f:
    f.write(line1); f.write(line2); f.write(line3); f.write(line4)
max_range = 50 # m
N = int(sys.argv[1])
for i in range(N):
    # 1. incriment time ( t = t0 + i)
    # 2. create random position (np.random.uniform)
    # 3. create spectrum from guassian with random params

    t = t0 + i
    lon = np.random.uniform(lon0-4.4e-4,lon0+4.4e-4)
    #lat = np.random.uniform(lat0-4.4e-4,lat0+4.4e-4)
    x = r_earth*(lon-lon0)*np.pi/180
    dy = np.sqrt(max_range**2-x**2)
    y = np.random.uniform(-dy,dy)
    lat = 180*y/(np.pi*r_earth)+lat0
    alt = np.sqrt(max_range**2-x**2-y**2)
    pos_str = str(lat)+','+str(lon)+','+str(alt)
    spec = Guassian(35,0,20,x,y)-35
    spec_str = ','.join(map(str,[spec]*19))
    with open(outFile,'ab') as f:
        f.write(str(t)+','+pos_str+','+spec_str+'\n')
