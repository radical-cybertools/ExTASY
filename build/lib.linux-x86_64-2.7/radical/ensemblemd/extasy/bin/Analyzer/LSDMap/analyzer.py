__author__ = 'vivek'

from radical.ensemblemd.mdkernels import MDTaskDescription
import time
import radical.pilot
import os

def Analyzer(umgr,RPconfig,Kconfig,cycle):

    print 'Starting Analysis'

    p1=time.time()
    curdir = os.path.dirname(os.path.realpath(__file__))
    mdtd=MDTaskDescription()
    mdtd.kernel="LSDMAP"
    mdtd.arguments = ['-l','-c','. run_analyzer.sh %s %s' %(Kconfig.nearest_neighbor_file,Kconfig.wfile)]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    lsdm=radical.pilot.ComputeUnitDescription()
    lsdm.pre_exec = mdtd_bound.pre_exec
    lsdm.pre_exec = ['echo 2 | trjconv -f %s -s %s -o tmpha.gro &>/dev/null'%(Kconfig.tmp_grofile,Kconfig.tmp_grofile)] + lsdm.pre_exec
    lsdm.pre_exec = ['module load gromacs'] + lsdm.pre_exec
    lsdm.executable = mdtd_bound.executable
    lsdm.arguments = mdtd_bound.arguments
    lsdm.input_staging = ['%s/%s'%(Kconfig.lsdm_config_loc,Kconfig.lsdm_config_name),Kconfig.tmp_grofile,'%s/run_analyzer.sh'%curdir]
    fname = Kconfig.tmp_grofile.split('.')[0]
    lsdm.output_staging = [' tmpha.eg > %s'%(Kconfig.egfile),'tmpha.ev > %s'%(Kconfig.evfile),Kconfig.nearest_neighbor_file,'lsdmap.log']

    lsdm.mpi = True
    lsdm.cores = RPconfig.PILOTSIZE

    lsdmCU = umgr.submit_units(lsdm)

    lsdmCU.wait()

    p2=time.time()

    print 'Analysis Execution time : ',(lsdmCU.stop_time - lsdmCU.start_time).total_seconds()
    print 'Total Analysis time : ',p2-p1

    curdir = os.path.dirname(os.path.realpath(__file__))

    if os.environ.get('PYTHONPATH') is None:
        os.environ['PYTHONPATH'] = curdir
    else:
        os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':%s'%curdir

    os.system('python %s/select.py %s -s %s -o %s' %(curdir,Kconfig.num_runs, Kconfig.evfile,Kconfig.num_clone_files))
    #Update Boltzman weights

    os.system('python %s/reweighting.py -c %s -n %s -s %s -w %s -o %s --max_alive_neighbors=%s --max_dead_neighbors=%s' % (curdir,Kconfig.tmp_grofile,Kconfig.nearest_neighbor_file,Kconfig.num_clone_files,Kconfig.wfile,Kconfig.outgrofile_name,Kconfig.max_alive_neighbors,Kconfig.max_dead_neighbors))

    #Rename outputfile as inputfile for next iteration
    os.system('mv %s %s_%s'%(Kconfig.outgrofile_name,cycle+1,Kconfig.input_gro))

    print 'Analysis + Update time : ',time.time() - p1
    return
