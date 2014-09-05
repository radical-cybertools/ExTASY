import os


if __name__ == "__main__":

    os.system('/bin/bash -l -c "module load gromacs"')
    os.system('/bin/bash -l -c "module load openmpi"')
    os.system('/bin/bash -l -c "grompp -n index.ndx"')
    os.system('/bin/bash -l -c "mdrun"')
