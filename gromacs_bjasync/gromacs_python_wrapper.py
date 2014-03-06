import time
import os
import sys

def run_gromacs(pdbfile,runfile,emfile,ff,water):
    #Prepare :topology file
    os.system('/bin/bash -l -c "module load gromacs"')
    os.system('/bin/bash -l -c "pdb2gmx -f %s -ff %s -water %s"'%(pdbfile,ff,water))

    #Run energy minimization
    os.system('/bin/bash -l -c "grompp -f %s -p topol.top -c %s"'%(emfile,pdbfile))
    os.system('/bin/bash -l -c "mdrun"')
    os.system('/bin/bash -l -c "mv confout.gro after_em.gro"')

    #Run MD
    os.system('/bin/bash -l -c "grompp -f %s -p topol.top -c after_em.gro"'%runfile)
    os.system('/bin/bash -l -c "mdrun"')
    

if __name__ == "__main__":
    pdbfile = sys.argv[1]
    runfile = sys.argv[2]
    emfile  = sys.argv[3]
    ff = sys.argv[4]
    water = sys.argv[5]
    t1=time.time()
    run_gromacs(pdbfile,runfile,emfile,ff,water)
    t2=time.time()
    f1=open('/N/u/vivek91/tryout/exectime.txt','a')
    f1.write(str(t1)+'\n'+str(t2)+'\n')
    f1.close()

