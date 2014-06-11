__author__ = 'vivek'

from parameters import *
import time
import radical.pilot
import os
from config.config_file import lsdmap_loc

def Analyzer(umgr):

    lsdm_tasks = []
    p1 = time.time()
    lsdm = radical.pilot.ComputeUnitDescription()
    lsdm.executable = "python"
    lsdm.arguments = ['%s/lsdm.py -f %s -c %s' % (lsdmap_loc,config_file, structure_file)]
    lsdm.input_data = [config_file_loc, structure_file_loc]
    lsdm.output_data = [egfile,evfile,nearest_neighbor_file]
    lsdm.cores = 1
    umgr.submit_units(lsdm_tasks)
    umgr.wait_units()
    p2 = time.time()

    print 'Analysis Time : ', (p2-p1)

    p1 = time.time()
    #Select new points
    os.system('python select_new_points.py %s %s -np %s' % (evfile,num_clone_files,num_runs))

    #Update Boltzman weights
    os.system('python update_weights.py --max_alive_neighbors 10 %s %s %s %s %s %s' % (recovery_flag,tmp_grofile,nearest_neighbor_file,num_clone_files,temp_wfile,outgrofile_name))
    p2 = time.time()

    print 'Update Time : ', (p2-p1)

