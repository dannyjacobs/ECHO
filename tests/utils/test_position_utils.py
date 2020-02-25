from ECHO import position_utils as pos
import numpy as np
from scipy.interpolate import interp1d


def test_latlon2xy():
    R_EARTH = 6371000
    lat0 = 33.41865
    lon0 = -111.9295
    lats = [33.418570342,33.4184937453,33.4184231533]
    lons = [-111.929099532,-111.929122768,-111.9291605]
    ref_xy = [(44.535783751,-8.85871396),(41.951723423,-7.368175116),(37.755572439,-25.227506159)]
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
