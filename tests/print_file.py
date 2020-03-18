import numpy as np
import sys,time,os
import os.path

infile = sys.argv[1]
dt = float(sys.argv[2])
lines = [line.rstrip('\n') for line in open(infile)]

try:
    if os.path.isfile(infile.split('.')[0]+'_test.txt'):
        os.remove(infile.split('.')[0]+'_test.txt')
        print('\nRemoving '+infile.split('.')[0]+'_test.txt'+' ...')
    #while True:
    for line in lines:
        with open(infile.split('.')[0]+'_test.txt','ab') as outfile:
            outfile.write(line+'\n')
        time.sleep(dt)
except KeyboardInterrupt:
    print('\nRemoving '+infile.split('.')[0]+'_test.txt'+' ...')
    os.remove(infile.split('.')[0]+'_test.txt')
