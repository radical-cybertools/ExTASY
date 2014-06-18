__author__ = 'vivek'

from config.parameters import *
import time
import radical.pilot
import os

def Analyzer(umgr):


    p1=time.time()
    curdir = os.path.dirname(os.path.realpath(__file__))
    lsdm=radical.pilot.ComputeUnitDescription()
    lsdm.executable = '/bin/bash'
    lsdm.arguments = ['-l','-c','". run_analyzer.sh out.ev out.nc 10000"']
    lsdm.input_data = ['%s/config.ini'%curdir,'out.gro','%s/run_analyzer.sh'%curdir,'%s/select_new_points.py'%curdir]
    lsdm.cores = 16

    umgr.submit_units(lsdm)

    umgr.wait_units()

    p2=time.time()

    print 'Analysis time : ',p2-p1

    #Update Boltzman weights
    #os.system('python update_weights.py --max_alive_neighbors 10 %s %s %s %s %s %s' % (recovery_flag,tmp_grofile,nearest_neighbor_file,num_clone_files,temp_wfile,outgrofile_name))
    return
