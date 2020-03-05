from ECHO import position_utils as pos
import numpy as np
from scipy.interpolate import interp1d


def test_latlon2xy():
    R_EARTH = 6371000
    lat0 = 33.41865
    lon0 = -111.9295
    lats = [33.41857,33.41849,33.41842]
    lons = [-111.92909,-111.92912,-111.92916]
    ref_xy = [(45.58991,-8.89559),(42.25407,-17.79118),(37.80627,-25.57483)]
    out_xy = []
    for i, lat in enumerate(lats):
        out_xy.append(pos.latlon2xy(lats[i],lons[i],lat0,lon0))
    assert np.allclose(ref_xy, out_xy, rtol=0, atol = 1e-3)


def test_to_spherical():
    x = 33.41865
    y = -111.9295
    z = 20.83333
    ref_spherical = (118.6551591,1.39430266,-1.280653130)
    out_spherical = pos.to_spherical(x,y,z)
    assert np.allclose(ref_spherical, out_spherical, rtol=0, atol = 1e-3)
