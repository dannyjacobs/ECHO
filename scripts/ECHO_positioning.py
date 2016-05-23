import numpy as np

R_EARTH = 6371000 # meters

def latlon2xy(lat,lon,lat0,lon0):
    x = R_EARTH*(lon - lon0)*(np.pi/180)
    y = R_EARTH*(lat - lat0)*(np.pi/180)
    return x,y

def to_spherical(x,y,z):
    # x and y are cartesian coordinates
    # z is relative altitude
    rhos = np.sqrt(x**2+y**2+z**2)
    thetas = np.arccos(z/rhos) # Zentih angle
    phis = np.arctan2(y,x) # Azimuthal angle
    return rhos,thetas,phis
