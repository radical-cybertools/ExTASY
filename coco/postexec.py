__author__ = 'vivek'
import os
import sys

if __name__ == '__main__':
    print 'creating new crd files...'
    nreps = sys.argv[1]
    cycle = sys.argv[2]
    for rep in range(nreps):
        dict['rep'] = rep
        dict['path'] = os.path.dirname(os.path.abspath(__file__))
        dict['cycle'] = cycle
        #tl = script.Script()
        os.system('source leaprc.ff99SB')
        os.system('x = loadpdb {path}/rep0{rep}/pentaopt{cycle}.pdb'.format(**dict))
        os.system('saveamberparm x {path}/rep0{rep}/delete.me {path}/rep0{rep}/min{cycle}.crd'.format(**dict))
        os.system('quit')
        #tl.run('tleap -f {}')