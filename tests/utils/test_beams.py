import pytest

import ECHO
import numpy as np
from scipy.interpolate import interp1d
import os


'''
Tests to make:
*create simple test beams
*test that plots won't work on incorrect types (efield, hpx, power, etc)
*test

Beams use pyuvdata and/or healpy
'''
test_cst = os.path.abspath('.') +'/tests/data/Chiropter_NS_cst.txt'

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
def test_read_cst_beam():
    testbeam = ECHO.Beam(beam_type='efield')
    testbeam.read_cst_beam(test_cst, beam_type='efield', frequency=[70e6],
                   telescope_name='Chiropter', feed_name='BicoLOG', feed_version='1.0',
                   model_name = 'Chiropter_NS_2019', model_version='1.0', feed_pol='y')
    assert(testbeam.beam.data_array.shape == (2, 1, 2, 1, 37, 72))
    return
