__author__ = 'vivek'

from radical.ensemblemd.mdkernels import MDTaskDescription
import time
import radical.pilot
import os

def Analyzer(umgr,RPconfig,Kconfig,cycle):

    p1=time.time()
    curdir = os.path.dirname(os.path.realpath(__file__))
    mdtd=MDTaskDescription()
    mdtd.kernel="LSDMAP"
    mdtd.arguments = ['-l','-c','. run_analyzer.sh %s %s %s' %(Kconfig.tmp_grofile,Kconfig.nearest_neighbor_file,Kconfig.wfile)]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    lsdm=radical.pilot.ComputeUnitDescription()
    lsdm.pre_exec = mdtd_bound.pre_exec
    lsdm.executable = mdtd_bound.executable
    lsdm.arguments = mdtd_bound.arguments
    lsdm.input_data = ['%s/%s'%(Kconfig.lsdm_config_loc,Kconfig.lsdm_config_name),Kconfig.tmp_grofile,'%s/run_analyzer.sh'%curdir]
    fname = Kconfig.tmp_grofile.split('.')[0]
    lsdm.output_data = [' %s.eg > %s'%(fname,Kconfig.egfile),'%s.ev > %s'%(fname,Kconfig.evfile),Kconfig.nearest_neighbor_file]
    lsdm.mpi = True
    lsdm.cores = RPconfig.PILOTSIZE

    lsdmCU = umgr.submit_units(lsdm)

    lsdmCU.wait()

    p2=time.time()

    print 'Analysis Execution time : ',(lsdmCU.stop_time - lsdmCU.start_time).total_seconds()
    print 'Total Analysis time : ',p2-p1

    curdir = os.path.dirname(os.path.realpath(__file__))

    os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':%s'%curdir

    os.system('python %s/select.py %s -s %s -o %s' %(curdir,Kconfig.num_runs, Kconfig.evfile,Kconfig.num_clone_files))
    #Update Boltzman weights
    os.system('python %s/reweighting.py -c %s -n %s -s %s -w %s -o %s' % (curdir,Kconfig.tmp_grofile,Kconfig.nearest_neighbor_file,Kconfig.num_clone_files,Kconfig.wfile,Kconfig.outgrofile_name))

    #Rename outputfile as inputfile for next iteration
    os.system('mv %s %s/%s'%(Kconfig.outgrofile_name,Kconfig.input_gro_loc,Kconfig.input_gro))


    print 'Analysis + Update time : ',time.time() - p1
    return
