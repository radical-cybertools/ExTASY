__author__ = 'vivek'

import radical.pilot
from radical.ensemblemd.mdkernels import MDTaskDescription
import os
import time
import glob


def Simulator(umgr,RPconfig,Kconfig,cycle,paths):

    curdir = os.path.dirname(os.path.realpath(__file__))

    print 'Cycle %s' %cycle
    grompp_name = os.path.basename(Kconfig.mdp_file)
    topol_name = os.path.basename(Kconfig.top_file)
    ndxfile_name = os.path.basename(Kconfig.ndx_file)

    nsave = Kconfig.nsave

    print 'Starting Simulation'

    gromacs_tasks = []
    for i in range(0, Kconfig.num_CUs):
        mdtd = MDTaskDescription()
        mdtd.kernel = "GROMACS"
        if Kconfig.grompp_options is not None:
            grompp_opts = Kconfig.grompp_options
        else:
            grompp_opts = ''
        if Kconfig.mdrun_options is not None:
            mdrun_opts = Kconfig.mdrun_options
        else:
            mdrun_opts = ''
        if ndxfile_name is not None:
            ndx_opts = Kconfig.ndxfile_name
        else:
            ndx_opts = ''
        mdtd.arguments = ['-l','-c','export grompp_options="%s" mdrun_options="%s" ndxfile="%s" && . run.sh %s start.gro %s out.gro %s' % (grompp_opts,mdrun_opts,ndx_opts,grompp_name,topol_name,Kconfig.num_cores_per_sim_cu)]
        mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
        gromacs_task = radical.pilot.ComputeUnitDescription()
        gromacs_task.pre_exec = mdtd_bound.pre_exec
        gromacs_task.executable = '/bin/bash'
        gromacs_task.arguments = mdtd_bound.arguments
        gromacs_task.mpi = True
        gromacs_task.cores = Kconfig.num_cores_per_sim_cu

        #gromacs_task.input_staging = ['%s/run.sh > run.sh'%curdir,'%s/temp/start%s.gro > start.gro' % (os.getcwd(), i),'%s' % (Kconfig.mdp_file), '%s' % (Kconfig.top_file)]
        inputs = ['ln -s %s/run.sh .'%paths[0],'ln -s %s/start%s.gro start.gro'%(paths[cycle],i),'ln -s %s/%s .'%(paths[0],grompp_name),'ln -s %s/%s .'%(paths[0],topol_name)]
        gromacs_task.pre_exec = gromacs_task.pre_exec + inputs

        if Kconfig.ndx_file is not None:
            #gromacs_task.input_staging.append('%s' % Kconfig.ndx_file)
            gromacs_task.pre_exec = gromacs_task.pre_exec + ['ln -s %s/%s .'%(paths[0],ndxfile_name)]
        if Kconfig.itp_file_loc is not None:
            # for itpfile in glob.glob(Kconfig.itp_file_loc + '*.itp'):
            #    gromacs_task.input_staging.append('%s' % itpfile)
            gromacs_task.pre_exec = gromacs_task.pre_exec + ['ln -s %s/*.itp .' % paths[0]]
        #gromacs_task.output_staging = ['out.gro > out%s.gro' % i]
        gromacs_task.post_exec = ['ln -s out.gro %s/out%s.gro'%(paths[cycle],i)]

        gromacs_tasks.append(gromacs_task)

    units = umgr.submit_units(gromacs_tasks)

    start_times = []
    end_times = []

    # Wait for all compute units to finish.
    umgr.wait_units()
    '''

    '''
    try:
        for unit in units:
            #print 'Start : ', unit.start_time, 'Stop : ', unit.stop_time
            start_times.append(unit.start_time)
            end_times.append(unit.stop_time)
    
        print 'Simulation Execution Time : ', (max(end_times)-min(start_times)).total_seconds()

    except:
        pass
