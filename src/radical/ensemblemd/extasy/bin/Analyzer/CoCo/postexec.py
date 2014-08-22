__author__ = 'vivek'
import os
import sys
from extasy import script

if __name__ == '__main__':
    print 'creating new crd files...'
    nreps = int(sys.argv[1])
    cycle = int(sys.argv[2])
    dict = {}
    for rep in range(nreps):
        dict['rep'] = rep
        dict['path'] = os.path.dirname(os.path.abspath(__file__))
        dict['cycle'] = cycle
        tl = script.Script()
        tl.append('source leaprc.ff99SB')
        tl.append('x = loadpdb {path}/rep0{rep}/pentaopt{cycle}.pdb'.format(**dict))
        tl.append('saveamberparm x {path}/rep0{rep}/delete.me {path}/rep0{rep}/min{cycle}.crd'.format(**dict))
        tl.append('quit')
        tl.run('tleap -f {}')
