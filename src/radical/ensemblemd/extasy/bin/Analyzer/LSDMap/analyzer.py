__author__ = 'vivek'

from config.RP_config import *
from radical.ensemblemd.mdkernels import MDTaskDescription
import time
import radical.pilot
import os

def Analyzer(umgr):


    p1=time.time()
    curdir = os.path.dirname(os.path.realpath(__file__))
    mdtd=MDTaskDescription()
    mdtd.kernel="LSDMAP"
    mdtd.arguments = ['-l','-c','". run_analyzer.sh"']
    mdtd_bound = mdtd.bind(resource=REMOTE_HOST)
    lsdm=radical.pilot.ComputeUnitDescription()
    lsdm.pre_exec = mdtd_bound.pre_exec
    lsdm.executable = mdtd_bound.executable
    lsdm.arguments = mdtd_bound.arguments
    lsdm.input_data = ['%s/config.ini'%curdir,'out.gro','%s/run_analyzer.sh'%curdir]
    lsdm.cores = 16

    umgr.submit_units(lsdm)

    umgr.wait_units()

    p2=time.time()

    print 'Analysis time : ',p2-p1

    #Update Boltzman weights
    #os.system('python update_weights.py --max_alive_neighbors 10 %s %s %s %s %s %s' % (recovery_flag,tmp_grofile,nearest_neighbor_file,num_clone_files,temp_wfile,outgrofile_name))
    return
