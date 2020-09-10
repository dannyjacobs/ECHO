import pytest

import ECHO
import numpy as np
from scipy.interpolate import interp1d


'''
Tests to make:
*create simple test beams
*test that plots won't work on incorrect types (efield, hpx, power, etc)
*test

Beams use pyuvdata and/or healpy
'''

def test_createBeam():
    #test that beams can't be made with invalid beam types
    with pytest.raises(AssertionError):
        testbeam=ECHO.Beam(beam_type='hpx')

    #make a beam with each valid beam_type
    testbeam=ECHO.Beam(beam_type='healpy')
    testbeam=ECHO.Beam(beam_type='efield')
    testbeam=ECHO.Beam(beam_type='power')

    return

def test_beamplots():
    testbeam = ECHO.Beam(beam_type='healpy') #has no beams yet, plotting should fail
    with pytest.raises(AssertionError):
        testbeam.plot_efield()
        testbeam.plot_efield_interp()
        testbeam.plot_power()
        testbeam.plot_power_interp()
        testbeam.plot_escatter()
        testbeam.plot_escatter_interp()
        testbeam.plot_powscatter()
        testbeam.plot_powscatter_interp()

    return
