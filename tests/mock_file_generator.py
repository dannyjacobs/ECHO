import numpy as np
import healpy as hp
import sys,optparse

o = optparse.OptionParser()
o.set_description('Generates a mock file for testing ECHO code and libraries.  \
Mimics a drone flying in a spiral pattern at a fixed distance from an antenna.  \
Uses Healpix pixel ordering and nsides parameter for generation of data.')
o.add_option('--nsides',type=int,default=8,
    help='Dictates number of sides in Healpix map => number of generated data points')
opts,args = o.parse_args(sys.argv[1:])


def Guassian_2d(a,b,c,x,y):
    return a*np.exp(-((x-b)**2+(y-b)**2)/(2*c**2))


outFile = 'exemplary_output_file.txt'
with open(outFile,'wb') as f:
   print('New file created: ',outFile)

R_E = 6.3781e6
freqs = [137.505,137.51,137.515,137.519,137.524,\
            137.529,137.534,137.539,137.544,137.549,\
            137.554,137.559,137.563,137.568,137.573,\
            137.578,137.583,137.588,137.593,137.598]
lat0,lon0 = 33.41865,-111.9295
t0 = 1145210544.0
line1 = '# Accumulated data for 20_04_2016, 11:02:55\n'
line2 = '# Column Format: 1 Time [GPS s], 2 Lat [deg], 3 Lon [deg],\
4 Rel Alt [m], 5: Radio Spectrum\n'
line3 = '# lat0,lon0: '+str(lat0)+','+str(lon0)+'\n'
line4 = '# Freqs: '+','.join(map(str,freqs))+'\n'
with open(outFile,'ab') as f:
    f.write(line1); f.write(line2); f.write(line3); f.write(line4)
max_range = 50 # m
nsides = opts.nsides
npix = hp.nside2npix(nsides)
thetas,phis = hp.pix2ang(nsides,map(int,np.linspace(0,npix,npix+1)))
thetas = thetas[::-1]; phis = phis[::-1]
rad_height = 3*np.pi/8
phis = phis[thetas<=rad_height]
thetas = thetas[thetas<=rad_height]
xs = np.linspace(-1,0.9,len(freqs))
for i,[theta,phi] in enumerate(zip(thetas,phis)):
    t = t0 + i
    x = max_range*np.cos(phi)*np.sin(theta)
    y = max_range*np.sin(phi)*np.sin(theta)
    lon = 180/(R_E*np.pi)*x+lon0
    lat = 180/(R_E*np.pi)*y+lat0
    alt = max_range*np.cos(theta)
    pos_str = str(lat)+','+str(lon)+','+str(alt)
    power = Guassian_2d(35,0,20,x,y)
    spec = power*np.exp(-10**2*xs**2)-90
    spec_str = ','.join(map(str,spec))
    with open(outFile,'ab') as f:
        f.write(str(t)+','+pos_str+','+spec_str+'\n')
