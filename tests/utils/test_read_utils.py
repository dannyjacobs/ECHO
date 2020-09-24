import pytest

import ECHO
import numpy as np
import os


'''
Tests to make:
*ulog read
*tlog read
*CST read
*rx read

'''
test_tlog = os.path.abspath('.') +'/tests/data/Shortened_NSTop_tlog.txt'
test_cst = os.path.abspath('.') +'/tests/data/Chiropter_NS_cst.txt'
test_rx = os.path.abspath('.') +'/tests/data/NSTop_rxdata.hdf5'

def test_os():
    print('/nTest Directory: ' + os.getenv('PYTEST_CURRENT_TEST'))
    print('/nrootdir: ' + os.path.abspath('.'))
    return

def test_tlog_read():
    wpt_array, global_array, local_array, gps_array = ECHO.read_utils.read_tlog_txt(test_tlog)
    #assert
    return

def test_ulog_read():
    #can test the CSV reads, but the ulog reads require a full .ulog file and those are pretty big.
    return

def test_read_h5():
    #Test that our
    assert(os.path.isfile(test_rx) == True)
    datadict = ECHO.read_utils.read_h5(test_rx)
    keylist=[]
    for key in datadict['Observation1'].keys():
        keylist.append(key)
    assert(len(keylist)==3)
    assert(keylist[0]=='Tuning1')
    assert(keylist[1]=='Tuning2')
    assert(keylist[2]=='time')
    return

def test_cst_to_hp():

    return

def test_read_cst_puv():
    testhpmap = ECHO.read_utils.CST_to_hp(test_cst, outfile=os.path.abspath('.') +'/tests/data/Chiropter_NS_cst.fits')
    return
