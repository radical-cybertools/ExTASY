__author__ = 'vivek'

from radical.ensemblemd.mdkernels import MDTaskDescription
import saga
import radical.pilot
import os

def Analyzer(umgr,RPconfig,Kconfig,cycle,paths):

    print 'Starting Analysis'
    MY_STAGING_AREA = 'staging:///'

    nearest_neighbor_file = 'neighbors.nn'
    egfile = 'tmpha.eg'
    evfile = 'tmpha.ev'
    num_clone_files = 'ncopies.nc'
    outgrofile_name = 'out.gro'

    curdir = os.path.dirname(os.path.realpath(__file__))
    mdtd=MDTaskDescription()
    mdtd.kernel="LSDMAP"
    mdtd.arguments = ['lsdm.py','-f','config.ini','-c','tmpha.gro','-n','%s'%nearest_neighbor_file,'-w','%s' %Kconfig.w_file]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    lsdm=radical.pilot.ComputeUnitDescription()
    lsdm.pre_exec = ['module load gromacs']
    lsdm.pre_exec = lsdm.pre_exec + ['python pre_analyze.py %s %s %s'%(Kconfig.num_CUs,Kconfig.md_output_file,paths[cycle])]
    lsdm.pre_exec = lsdm.pre_exec + ['echo 2 | trjconv -f %s -s %s -o tmpha.gro'%(Kconfig.md_output_file,Kconfig.md_output_file)]
    lsdm.pre_exec = lsdm.pre_exec + mdtd_bound.pre_exec
    lsdm.executable = mdtd_bound.executable
    lsdm.arguments = mdtd_bound.arguments

    pre_ana_stage = {
                        'source': MY_STAGING_AREA + 'pre_analyze.py',
                        'target': 'pre_analyze.py',
                        'action': radical.pilot.LINK
                    }

    config_stage = {
                        'source': MY_STAGING_AREA + 'config.ini',
                        'target': 'config.ini',
                        'action': radical.pilot.LINK
                    }

    ana_stage = {
                        'source': MY_STAGING_AREA + 'run_analyzer.sh',
                        'target': 'run_analyzer.sh',
                        'action': radical.pilot.LINK
                }

    lsdm.input_staging = [pre_ana_stage,config_stage,ana_stage]

    if(cycle>0):
        #lsdm.input_staging = lsdm.input_staging + [Kconfig.w_file]
        lsdm.pre_exec = lsdm.pre_exec + ['ln %s/%s .'%(paths[cycle],os.path.basename(Kconfig.w_file))]

    lsdm.mpi = True
    lsdm.cores = RPconfig.PILOTSIZE

    lsdmCU = umgr.submit_units(lsdm)

    lsdmCU.wait()

    lsdm_path=saga.Url(lsdmCU.working_directory).path

    print 'Select + Reweighting step'

    post=radical.pilot.ComputeUnitDescription()
    post.pre_exec = mdtd_bound.post_exec + ['ln %s/post_analyze.py .'%paths[0],'ln %s/select.py .'%paths[0],'cp -r %s/lsdmap .'%paths[0],
                      'ln %s/reweighting.py .'%paths[0],'ln %s/%s .'%(lsdm_path,nearest_neighbor_file),
                      'ln %s/%s .'%(lsdm_path,evfile),'ln %s/%s .'%(lsdm_path,Kconfig.md_output_file)]
    if(cycle>=1):
        post.pre_exec = post.pre_exec +['cp %s/%s .'%(lsdm_path,Kconfig.w_file)]
    post.executable = 'python'
    post.arguments = ['post_analyze.py',Kconfig.num_runs,evfile,num_clone_files,Kconfig.md_output_file,nearest_neighbor_file,
                         Kconfig.w_file,outgrofile_name,Kconfig.max_alive_neighbors,Kconfig.max_dead_neighbors,
                         os.path.basename(Kconfig.md_input_file),cycle]

    #lsdm.output_staging = [' tmpha.eg > %s'%(egfile),'tmpha.ev > %s'%(evfile),nearest_neighbor_file,'lsdmap.log']
    if((cycle+1)%Kconfig.nsave==0):
        post.post_exec = ['ln %s/lsdmap.log .'%lsdm_path]
        post.post_exec = post.post_exec + ['ln %s %s/'%(Kconfig.w_file,paths[cycle]),'ln %s_%s %s/%s_%s'%(cycle+1,os.path.basename(Kconfig.md_input_file),paths[cycle],cycle+1,os.path.basename(Kconfig.md_input_file))]
        post.output_staging = ['lsdmap.log',Kconfig.w_file,'%s_%s'%(cycle+1,os.path.basename(Kconfig.md_input_file))]
    else:
        post.post_exec = ['ln %s %s/'%(Kconfig.w_file,paths[cycle]),'ln %s_%s %s/%s_%s'%(cycle+1,os.path.basename(Kconfig.md_input_file),paths[cycle],cycle+1,os.path.basename(Kconfig.md_input_file))]


    postCU = umgr.submit_units(post)
    postCU.wait()

    try:
        print 'Analysis Execution time : ',((lsdmCU.stop_time - lsdmCU.start_time).total_seconds()+(postCU.stop_time - postCU.start_time).total_seconds())

    except:
        pass

    return
