__author__ = 'vivek'

from config.RP_config import *
from config.kernel_config import *
from radical.ensemblemd.mdkernels import MDTaskDescription
import time
import radical.pilot
import os

def Analyzer(umgr):


    p1=time.time()
    curdir = os.path.dirname(os.path.realpath(__file__))
    mdtd=MDTaskDescription()
    mdtd.kernel="LSDMAP"
    mdtd.arguments = ['-l','-c','. run_analyzer.sh %s %s %s' %(tmp_grofile,nearest_neighbor_file,wfile)]
    mdtd_bound = mdtd.bind(resource=REMOTE_HOST)
    lsdm=radical.pilot.ComputeUnitDescription()
    lsdm.pre_exec = mdtd_bound.pre_exec
    lsdm.executable = mdtd_bound.executable
    lsdm.arguments = mdtd_bound.arguments
    lsdm.input_data = ['%s/config.ini'%lsdm_config,tmp_grofile,'%s/run_analyzer.sh'%curdir]
    fname = tmp_grofile.split('.')[0]
    lsdm.output_data = [' %s.eg > %s'%(fname,egfile),'%s.ev > %s'%(fname,evfile),nearest_neighbor_file]
    lsdm.mpi = True
    lsdm.cores = PILOTSIZE

    umgr.submit_units(lsdm)

    umgr.wait_units()

    p2=time.time()

    print 'Analysis time : ',p2-p1

    os.system('python %s/select.py %s -s %s -o %s' %(curdir,num_runs, evfile,num_clone_files))
    #Update Boltzman weights
    os.system('python %s/reweighting.py -c %s -n %s -s %s -w %s -o %s' % (curdir,tmp_grofile,nearest_neighbor_file,num_clone_files,wfile,outgrofile_name))
    return
