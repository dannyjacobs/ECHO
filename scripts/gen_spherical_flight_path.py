#! /usr/bin/env python
import numpy as n,sys,os
import optparse, healpy
from pylab import *
from flight_planning import print_MAV_WPT,print_MAV_YAW,APM_PLANNER_FILE_HEADER,R_earth,length
"""
Input some basic parameters to

Output a new waypoint file for a spherical flight with waypoints on a healpix grid starting from the set CURRENT POSITION near the dish.

test usage: python gen_spherical_flight_path_v3.py --radius=100 --min_height=6 --center="34.61995_-112.45059" --file_prefix="test_flightpath" --nside=16 --velocity=1 --max_points=999999 --sortie_length=30
"""

o = optparse.OptionParser()
o.set_description('''Generates a waypoint file for a series of concentric circles stacked to make constant _distance_ flight.''')
o.add_option('--radius',type=float,
    help='distance from antenna under test [m]')
#o.add_option('--norbits',type=int,
#    help='number of circles to execute')
o.add_option('--min_height',type=float,
    help='the base level of the lowest pass [m]')
o.add_option('--center',type=str,
   help='lat_lon of antenna under test in degrees [REQUIRED]')
#o.add_option('--delta_el',type=float,
#    help='angular elevation seperation between flight levels [deg]')
#o.add_option('--delta_az',type=float,
#    help='angular azimuth separation between circle waypoints [deg]')
o.add_option('--velocity',type=float,
    help='WPT_NAV velocity setting in m/s')
o.add_option('--file_prefix',type=str,
    help='output filename')
o.add_option('--sortie_length',type=float,
    help='break the total pattern into sorties of this length [minutes]')
o.add_option('--nside',type=int,
    help='the nside of the desired healpix point grid')
o.add_option('--max_points',type=int,default=75,
    help='max number of points to put in the file. a pm planner 2 gets unreliable above 80. default=75')
o.add_option('--pol_angle',type=float,default=0,
    help='angle of dipole wrt north [deg]')
#o.add_option('--stripe_spacing',type=float,default=10,
#    help=' Default is 10m')
#o.add_option('--nstripes',type=int,
#    help='number of stripes [REQUIRED]')
#o.add_option('--length',type=float,
#    help='Length of stripes in meters [REQUIRED]')
#o.add_option('--alt',type=float,
#    help='alt in meters [REQUIRED]')
opts,args = o.parse_args(sys.argv[1:])

#parse inputs
center_lat,center_lon = map(float,opts.center.split('_'))
#random point near dish
current_waypoint = "34.619813_-112.4504370_6" 



#add a check that the target location is less than 100m from the launch position.
current_lat,current_lon,current_alt = map(float,current_waypoint.split("_"))
ant_to_pos_dist = n.sqrt(((current_lat-center_lat)*n.pi/180*R_earth)**2+
                        ((current_lon-center_lon)*n.pi/180*R_earth)**2)#+
                        #current_alt**2)
if ant_to_pos_dist > 1000:
    print "ERROR distance between target location ({p} m) and starting uav position is > 100m".format(ant_to_pos_dist)
    print "Exiting...."
    sys.exit()

#RADIAN conversion!!!
#DELTA_ELEVATION = opts.delta_el*n.pi/180
#DELTA_AZIMUTH=opts.delta_az*n.pi/180
# ------ below this point everything is in RADIANS ------
# -----  (we'll print everything in degrees at the end) --



pixnums = n.arange(healpy.nside2npix(opts.nside))
co_els,azimuths = healpy.pix2ang(opts.nside,pixnums,nest=False)
elevations = n.pi/2 - co_els




print "computing elevation coverage"
min_el = opts.min_height/opts.radius
elevation_range = n.pi/2 - min_el
g = elevations>min_el
elevations = elevations[g]
azimuths = azimuths[g]
print "Generating healpix grid with {n} points".format(n=len(azimuths))
print "min elevation = {min}, max elevation = {max}".format(
    min=elevations.min()*180/n.pi,max=elevations.max()*180/n.pi)

altitude_levels = n.sin(elevations)*opts.radius

print "computing altitudes in range: {min} - {max} meters".format(min=altitude_levels.min(),max=altitude_levels.max())
coords = []
#for each circle
#for i,alt in enumerate(altitude_levels):
#    el = elevations[i]
#    for az in azimuths:
#        coords.append([opts.radius*n.cos(el)*n.cos(az),
#        opts.radius*n.cos(el)*n.sin(az),
#        alt])
X = opts.radius*n.cos(elevations)*n.cos(azimuths)
Y = opts.radius*n.cos(elevations)*n.sin(azimuths)
Z = altitude_levels
#coords = n.array(coords)
coords = n.vstack((X,Y,Z)).T
coords = n.flipud(coords)
print coords.shape
subplot(211)
plot(coords[:,0],coords[:,1])
subplot(212)
plot(coords[:,1],coords[:,2])
show()

#estimate total flying distance
flight_distance = 0
distances = []
for i in xrange(1,len(coords)):
    distances.append(length(coords[i]-coords[i-1]))
    flight_distance += length(coords[i]-coords[i-1])
print "total flight distance = {dist} [m]".format(dist=flight_distance)
print "estimated flying time at {vel} m/s ={time} [minutes]".format(
            vel=opts.velocity,time=flight_distance//opts.velocity/60)



#covert to lat, lon in radians
coords[:,:2] /= R_earth

#converting final coordinates to DEGREES
# from here all units are lat/lon degrees and meters
coords[:,:2] *= 180/n.pi
# add offset to center pattern over target location
coords[:,0] += center_lat
coords[:,1] += center_lon

header_lines = []
#print "QGC WPL 110"
header_lines.append(APM_PLANNER_FILE_HEADER)
offset = 0
#header_lines.append(current_waypoint.strip())
offset +=1
#print pointing (sets the polarization)
header_lines.append(str(offset)+'\t'+print_MAV_YAW(center_lat,center_lon,50,angle=opts.pol_angle-90,ROI_distance=5e3))
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
        print "writing position file:",outfile, "with ",len(lines),"waypoints"
        outlines = header_lines+lines
        outlines = [l+'\n' for l in outlines]
        open(outfile,'w').writelines(outlines)
        sortie_count += 1
        lines = []
        current_length = 0
        offset = header_offset
    lines.append(str(offset)+'\t'+print_MAV_WPT(coord[0],coord[1],coord[2]))
    offset += 1
outfile = opts.file_prefix+'_sortie'+str(sortie_count)+'.txt'
print "writing position file:",outfile, "with ",len(lines),"waypoints"
outlines = header_lines+lines
outlines = [l+'\n' for l in outlines] #add a cr to each line
open(outfile,'w').writelines(outlines)
