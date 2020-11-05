import pytest

import ECHO
import numpy as np
from scipy.interpolate import interp1d


'''
Tests to make:
*test that object initializes properly

Beams use pyuvdata and/or healpy
'''
lat, lon = (33.448376, -112.074036)
frequency = 75.00
description = "This is an observation object."

def test_createObs():
    #test that observations are created properly
    testobs = ECHO.Observation(lat, lon, frequency, description)
    assert (testobs.lat == lat), "Latitude not correct."
    assert (testobs.lon == lon), "Longitude not correct."
    assert (testobs.ref_frequency == frequency), "Frequency not correct."
    assert (testobs.description == description), "Description not correct."
    return

def test_sortieList():
    #test that the sortie list increments properly
    testobs = ECHO.Observation(lat, lon, frequency, description)
    testobs.addSortie(tlog='tlog_file', ulog='ulog_file', data='rx_data_file')
    assert (len(testobs.sortie_list)==1)
    assert (testobs.num_sorties ==1)
    return
