#! /usr/bin/env python
import numpy as n
def length(x):
    #compute the length of a vector
    return n.sqrt(n.dot(x,x))

def print_MAV_WPT(lat,lon,alt,spline=False):
    "generate the string commonly accepted by mission planner et al"
    """see https://pixhawk.ethz.ch/mavlink/ and
    http://qgroundcontrol.org/mavlink/waypoint_protocol
    and documented in Google Drive/ECHO/Memos/Programming_Auto_missions"""
    if spline:
        return "0\t3\t82\t0\t0\t0\t0\t{lat:18.16f}\t{lon:18.15f}\t{alt:18.16f}\t1".format(
                lat=lat,lon=lon,alt=alt)

    else: #use ordinary waypoint nav
        return "0\t3\t16\t0\t5\t0\t0\t{lat:18.16f}\t{lon:18.15f}\t{alt:18.16f}\t1".format(
                lat=lat,lon=lon,alt=alt)
def print_MAV_YAW(lat,lon,alt,angle,ROI_distance=1e3):
    "angle = degrees of nose from north"
    """
    create a Point of Interest at which the drone will point its nose
    If the POI is far enough away (currently set at 1km), drone will stay locked to this angle
    while it follows waypoints.

    Note that the distance has been kept small for testing purposes (on the 0.001% chance it tries to fly there for a
    first hand look.)
    """
    lat += n.cos(angle*n.pi/180)*ROI_distance/R_earth*180/n.pi
    lon += n.sin(angle*n.pi/180)*ROI_distance/R_earth*180/n.pi
    return "0\t3\t201\t0\t0\t0\t0\t{lat:18.16f}\t{lon:18.15f}\t{alt:18.16f}\t1".format(
                lat=lat,lon=lon,alt=alt)
APM_PLANNER_FILE_HEADER="QGC WPL 110"

"""
Earth radius from astropy.constants.R_earth
  Name   = Earth equatorial radius
  Value  = 6378136.0
  Error  = 0.5
  Units  = m
  Reference = Allen's Astrophysical Quantities 4th Ed.

"""

R_earth = 6378136.0
