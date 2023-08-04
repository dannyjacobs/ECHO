#! /usr/bin/env python
from __future__ import print_function
import numpy as n,sys
import optparse, healpy
from pylab import *
from flight_planning import print_MAV_WPT,APM_PLANNER_FILE_HEADER,R_earth,length
"""
Input some basic parameters to

Output a new waypoint file for a spherical flight with waypoints on a healpix grid starting from the set CURRENT POSITION near the dish.

10/3 usage: python gen_spherical_flight_path.py --min_height=20 --center="33.399685_-111.915271" --file_prefix="Chir_Meyer_Testpath" --yaw_angle=180
"""

o = optparse.OptionParser()
o.set_description('''Generates a waypoint file for a series of concentric circles stacked to make constant _distance_ flight.''')
o.add_option('--radius',type=float,default=100,
    help='distance from antenna under test [m]')
o.add_option('--min_height',type=float,default=6,
    help='the base level of the lowest pass [m]')
o.add_option('--center',type=str,
   help='lat_lon of antenna under test in degrees [REQUIRED]')
o.add_option('--velocity',type=float,default=2,
    help='WPT_NAV velocity setting in m/s')
o.add_option('--file_prefix',type=str,
    help='output filename')
o.add_option('--sortie_length',type=float,default=30,
    help='break the total pattern into sorties of this length [minutes]')
o.add_option('--nside',type=int,default=8,
    help='the nside of the desired healpix point grid')
o.add_option('--max_points',type=int,default=500,
    help='max number of points to put in the file. apm planner 2 got unreliable above 80.')
o.add_option('--pol_angle',type=float,default=0,
    help='angle of dipole wrt north [deg]')
o.add_option('--yaw_angle',type=float,default=0,
    help='angle the drone is point wrt north [deg]')
opts,args = o.parse_args(sys.argv[1:])

#parse inputs
center_lat,center_lon = map(float,opts.center.split('_'))

# ------ below this point everything is in RADIANS ----------
# -----  (we'll print everything in degrees at the end) -----
pixnums = n.arange(healpy.nside2npix(opts.nside)) #nside2npix=3072 when nside=16, so array from 0 to 3071
co_els,azimuths = healpy.pix2ang(opts.nside,pixnums,nest=False) #colatitude and longitude in radians
elevations = n.pi/2 - co_els #converts colatitude to latitude
#elevations go from pi at the north pole to -pi at the south pole
#azimuths go from 0 due north to 2pi all the way around

print("computing elevation coverage")
min_el = opts.min_height/opts.radius #typically 6/100
elevation_range = n.pi/2 - min_el #not used anywhere
g = elevations>min_el #an array that is the same length as elevations, with True in each index where elevation>min_el
elevations = elevations[g] #removes all elevations below min_el
azimuths = azimuths[g] #removes corresponding azimuths
print("Generating healpix grid with {n} points".format(n=len(azimuths)))
print("min elevation = {min}, max elevation = {max}".format(
    min=elevations.min()*180/n.pi,max=elevations.max()*180/n.pi))

altitude_levels = n.sin(elevations)*opts.radius #converts elevations into altitudes from min_el to radius

print("computing altitudes in range: {min} - {max} meters".format(min=altitude_levels.min(),max=altitude_levels.max()))
coords = []
X = opts.radius*n.cos(elevations)*n.cos(azimuths) #x coordinate in meters from center
Y = opts.radius*n.cos(elevations)*n.sin(azimuths) #y coordinate in meters from center
Z = altitude_levels #z coordinate in altitude
coords = n.vstack((X,Y,Z)).T #makes an array of [x,y,z] arrays
coords = n.flipud(coords) #puts the first waypoint first

print(coords.shape)
subplot(211)
plot(coords[:,0],coords[:,1])
subplot(212)
plot(coords[:,1],coords[:,2])
show()

#estimate total flying distance
flight_distance = 0
distances = []
for i in range(1,len(coords)):
    distances.append(length(coords[i]-coords[i-1])) #distance between each waypoint
    flight_distance += length(coords[i]-coords[i-1]) #running total of distance
print("total flight distance = {dist} [m]".format(dist=flight_distance))
print("estimated flying time at {vel} m/s ={time} [minutes]".format(
            vel=opts.velocity,time=flight_distance//opts.velocity/60))

#convert to lat, lon in radians
coords[:,:2] /= R_earth
#converting final coordinates to DEGREES
#from here all units are lat/lon degrees and meters
coords[:,:2] *= 180/n.pi
#add offset to center pattern over target location
coords[:,0] += center_lat
coords[:,1] += center_lon

#text file creation
header_lines = []
offset = 0
header_lines.append(APM_PLANNER_FILE_HEADER) #"QGC WPL 110"
offset +=1
header_offset = offset

current_length = 0
files = []
lines = []
sortie_count = 0
for i,coord in enumerate(coords):
    if i>0:
        #calculate length of current sortie in minutes
        current_length += distances[i-1]/opts.velocity/60
        #convert from deg lat/lon back to m
    if (current_length >= opts.sortie_length and not opts.sortie_length is None) or offset>opts.max_points:
        outfile = opts.file_prefix+'_sortie'+str(sortie_count)+'.txt'
        print(("writing position file:",outfile, "with ",len(lines),"waypoints"))
        outlines = header_lines+lines
        outlines = [l+'\n' for l in outlines]
        open(outfile,'w').writelines(outlines)
        sortie_count += 1
        lines = []
        current_length = 0
        offset = header_offset
    lines.append(str(offset)+'\t'+print_MAV_WPT(opts.yaw_angle,coord[0],coord[1],coord[2])) #probably adjust the MAV_WPT function to include yaw angle
    offset += 1
outfile = opts.file_prefix+'_sortie'+str(sortie_count)+'.txt'
print(("writing position file:",outfile, "with ",len(lines),"waypoints"))
outlines = header_lines+lines
outlines = [l+'\n' for l in outlines] #add a cr to each line
open(outfile,'w').writelines(outlines)
