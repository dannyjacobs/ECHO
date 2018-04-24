#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2018 Wylie Standage-Beier
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr
from time import time
from os.path import isfile
from numpy import complex64, float32, int32

_type_to_type = {
  complex: complex64,
  float: float32,
  int: int32,
}


class csvSink(gr.sync_block):
    """
    csvSink block writes data to a time stamped csv file
    """
    def __init__(self, labels, dtype, veclen, file, append):
        gr.sync_block.__init__(self,
            name="csvSink",
            in_sig=[(_type_to_type[dtype], veclen)],
            out_sig=None)
        if type(labels) is str:
            labels = labels.split(',')
        assert(isinstance(labels, list), 'labels must be a list')
        self.labels = labels
        self.veclen = veclen
        self.dtype = dtype
        assert(len(labels)==veclen, 'The number of labels must match the vector size of the input')
        firstLine = ','.join(['time']+[str(l) for l in labels])+'\n'
        self.fid = open(file, 'w')
        self.fid.write(firstLine)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        for i in range(0, len(in0)):
            outList = ['%.6f'%time()]
            outList += list(in0[i,:])
            lineOut = ','.join([str(oli) for oli in outList])+'\n'
            self.fid.write(lineOut)
        return len(input_items[0])


