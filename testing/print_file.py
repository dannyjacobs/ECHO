import numpy as np
import sys,time,os

infile = sys.argv[1]
dt = float(sys.argv[2])
lines = [line.rstrip() for line in open(infile)]

try:
    for line in lines:
        with open(infile.replace('sample','test'),'ab') as outfile:
            outfile.write(line+'\n')
        time.sleep(dt)
except KeyboardInterrupt:
    os.remove(infile.replace('sample','test'))
