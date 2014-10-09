__author__ = 'vivek'

from radical.ensemblemd.mdkernels import MDTaskDescription
import time
import radical.pilot
import os

def Analyzer(umgr,RPconfig,Kconfig,cycle):

    print 'Starting Analysis'
    nearest_neighbor_file = 'neighbors.nn'
    egfile = 'lsdmap.eg'
    evfile = 'lsdmap.ev'
    num_clone_files = 'ncopies.nc'
    outgrofile_name = 'out.gro'

    curdir = os.path.dirname(os.path.realpath(__file__))
    mdtd=MDTaskDescription()
    mdtd.kernel="LSDMAP"
    mdtd.arguments = ['-l','-c','. run_analyzer.sh %s %s' %(nearest_neighbor_file,Kconfig.w_file)]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    lsdm=radical.pilot.ComputeUnitDescription()
    lsdm.pre_exec = mdtd_bound.pre_exec
    lsdm.pre_exec = ['echo 2 | trjconv -f %s -s %s -o tmpha.gro &>/dev/null'%(Kconfig.md_output_file,Kconfig.md_output_file)] + lsdm.pre_exec
    lsdm.pre_exec = ['module load gromacs'] + lsdm.pre_exec
    lsdm.executable = mdtd_bound.executable
    lsdm.arguments = mdtd_bound.arguments
    lsdm.input_staging = [Kconfig.lsdm_config_file,Kconfig.md_output_file,'%s/run_analyzer.sh'%curdir]
    lsdm.output_staging = [' tmpha.eg > %s'%(egfile),'tmpha.ev > %s'%(evfile),nearest_neighbor_file,'lsdmap.log']
    if(cycle>0):
        lsdm.output_staging = lsdm.output_staging.extend(Kconfig.w_file)

    lsdm.mpi = True
    lsdm.cores = RPconfig.PILOTSIZE

    lsdmCU = umgr.submit_units(lsdm)

    lsdmCU.wait()

    if type(lsdmCU) != list:
        lsdmCU = [lsdmCU]

    for u in lsdmCU:
        if u.state != radical.pilot.DONE:
            print "CU {0} failed. Log: {1}".format(u.uid, u.log)
            raise Exception("CU {0} failed".format(u.uid))

    try:
        print 'Analysis Execution time : ',(lsdmCU.stop_time - lsdmCU.start_time).total_seconds()

    except:
        pass

    curdir = os.path.dirname(os.path.realpath(__file__))

    if os.environ.get('PYTHONPATH') is None:
        os.environ['PYTHONPATH'] = curdir
    else:
        os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':%s'%curdir

    os.system('python %s/select.py %s -s %s -o %s' %(curdir,Kconfig.num_runs,evfile,num_clone_files))
    #Update Boltzman weights

    os.system('python %s/reweighting.py -c %s -n %s -s %s -w %s -o %s --max_alive_neighbors=%s --max_dead_neighbors=%s' % (curdir,Kconfig.md_output_file,nearest_neighbor_file,num_clone_files,Kconfig.w_file,outgrofile_name,Kconfig.max_alive_neighbors,Kconfig.max_dead_neighbors))

    #Rename outputfile as inputfile for next iteration
    os.system('mv %s %s_%s'%(outgrofile_name,cycle+1,os.path.basename(Kconfig.md_input_file)))
    return
