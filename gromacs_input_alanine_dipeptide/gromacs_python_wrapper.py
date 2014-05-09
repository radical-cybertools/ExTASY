import time
import os
import sys

def run_gromacs():
    #Prepare :topology file
    os.system('/bin/bash -l -c "module load gromacs"')
    os.system('/bin/bash -l -c "pdb2gmx -f aladip.pdb -ff "amber03" -water none"')

    #Run energy minimization
    os.system('/bin/bash -l -c "grompp -f em.mdp -p topol.top -c aladip.pdb"')
    os.system('/bin/bash -l -c "mdrun"')
    os.system('/bin/bash -l -c "mv confout.gro after_em.gro"')

    #Run MD
    os.system('/bin/bash -l -c "grompp -f run.mdp -p topol.top -c after_em.gro"')
    os.system('/bin/bash -l -c "mdrun"')
    

if __name__ == "__main__":
    run_gromacs()    

