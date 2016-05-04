import sys

inFile = sys.argv[1]
outFile = 'example_accumulated_file.txt'
lines = open(inFile).readlines()
with open(outFile,'wb') as f:
    print 'New file created: %s' %outFile
for line in lines:
    if 'Error' in line:
        line = line.split(',')[0]+','+','.join(map(str,[-1]*22))+'\n'
    with open(outFile,'ab') as f:
        f.write(line)
