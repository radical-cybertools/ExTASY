__author__ = 'vivek'

from radical.ensemblemd.mdkernels import MDTaskDescription
import time
import radical.pilot
import os

def Analyzer(umgr,RPconfig,Kconfig,cycle,paths):

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
    lsdm.pre_exec = ['module load gromacs']
    lsdm.pre_exec = lsdm.pre_exec + ['ln -s %s/pre_analyze.py'%paths[0],'python pre_analyze.py %s %s %s'%(Kconfig.num_CUs,Kconfig.md_output_file,paths[cycle])]
    lsdm.pre_exec = lsdm.pre_exec + ['echo 2 | trjconv -f %s -s %s -o tmpha.gro &>/dev/null'%(Kconfig.md_output_file,Kconfig.md_output_file)]
    lsdm.pre_exec = lsdm.pre_exec + mdtd_bound.pre_exec
    lsdm.executable = mdtd_bound.executable
    lsdm.arguments = mdtd_bound.arguments
    #lsdm.input_staging = [Kconfig.lsdm_config_file,Kconfig.md_output_file,'%s/run_analyzer.sh'%curdir,'%s/lsdm.py'%curdir]
    lsdm.pre_exec = lsdm.pre_exec + ['ln -s %s/%s .'%(paths[0],Kconfig.lsdm_config_file),'ln -s %s/run_analyzer.sh .'% paths[0],'ln -s %s/lsdm.py .'%paths[cycle]]
    if(cycle>0):
        #lsdm.input_staging = lsdm.input_staging + [Kconfig.w_file]
        lsdm.pre_exec = lsdm.pre_exec + ['cp %s/%s .'%(paths[cycle-1],os.path.basename(Kconfig.w_file))]

    #lsdm.output_staging = [' tmpha.eg > %s'%(egfile),'tmpha.ev > %s'%(evfile),nearest_neighbor_file,'lsdmap.log']
    lsdm.post_exec = ['wait','ln -s %s/post_analyze.py .'%paths[0],'ln -s %s/select.py .'%paths[0],'cp -r %s/lsdmap .'%paths[0],
                      'ln -s %s/reweighting.py .'%paths[0],
                      'python post_analyze.py %s %s %s %s %s %s %s %s %s %s %s'%
                        (Kconfig.num_runs,evfile,num_clone_files,Kconfig.md_output_file,nearest_neighbor_file,
                         Kconfig.w_file,outgrofile_name,Kconfig.max_alive_neighbors,Kconfig.max_dead_neighbors,
                         Kconfig.md_input_file,cycle)]

    #lsdm.output_staging = [' tmpha.eg > %s'%(egfile),'tmpha.ev > %s'%(evfile),nearest_neighbor_file,'lsdmap.log']
    if((cycle+1)%Kconfig.nsave==0):
        lsdm.output_staging = ['lsdmap.log',Kconfig.w_file,'%s_%s'%(cycle+1,Kconfig.md_input_file)]
    else:
        lsdm.post_exec = lsdm.post_exec + ['cp %s %s/'%(Kconfig.w_file,paths[cycle]),'ln -s %s_%s %s/'%(cycle+1,Kconfig.md_input_file,paths[cycle])]

    lsdm.mpi = True
    lsdm.cores = RPconfig.PILOTSIZE

    lsdmCU = umgr.submit_units(lsdm)

    lsdmCU.wait()

    try:
        print 'Analysis Execution time : ',(lsdmCU.stop_time - lsdmCU.start_time).total_seconds()

    except:
        pass

    return
