#!/bin/bash

evfile=$1
ncfile=$2
nruns=$3

PYTHONPATH=/home/vb17/gromacs_sim_test/

/N/soft/python/2.7/bin/python /home/vb17/lsdmap/lsdmap/lsdm.py -f config.ini -c out.gro

/N/soft/python/2.7/bin/python select_new_points.py $evfile $ncfile --np $nruns


